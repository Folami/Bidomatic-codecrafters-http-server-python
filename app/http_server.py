import socket
import threading
import os
import sys
from app.http_client import HttpClient


class HttpServer:
    def __init__(self, args, port=4221):
        self.port = port
        self.files_directory = None
        self.parse_command_line_args(args)

    def parse_command_line_args(self, args):
        for i in range(len(args)):
            if args[i] == "--directory" and i + 1 < len(args):
                self.files_directory = args[i + 1]
                if not os.path.exists(self.files_directory) or not os.path.isdir(self.files_directory):
                    print("Error: Provided directory does not exist or is not valid.", file=sys.stderr)
                    sys.exit(1)

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('', self.port))
            server_socket.listen()
            print(f"Server listening on port: {self.port}")
            
            while True:
                client_socket, addr = server_socket.accept()
                print(f"Accepted connection from {addr[0]}:{addr[1]}")
                client_handler = HttpClient(client_socket, self)
                threading.Thread(target=client_handler.run).start()

    def process_request(self, request, response):
        path = request.get_path()
        method = request.get_method()
        
        if path in ["/", "/index.html"]:
            self.handle_root_endpoint(response)
        elif path.startswith("/echo/"):
            self.handle_echo_endpoint(request, response)
        elif path == "/user-agent":
            self.handle_user_agent_endpoint(request, response)
        elif path.startswith("/files/"):
            self.handle_files_endpoint(request, response)
        else:
            response.write("HTTP/1.1 404 Not Found\r\n\r\n")

    def handle_root_endpoint(self, response):
        response.write("HTTP/1.1 200 OK\r\n\r\n")

    def handle_echo_endpoint(self, request, response):
        echo_body = request.get_path()[6:]  # Strip "/echo/"
        body_bytes = echo_body.encode('utf-8')
        headers = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n"
        if request.client_accepts_gzip():
            headers += "Content-Encoding: gzip\r\n"
        headers += f"Content-Length: {len(body_bytes)}\r\n\r\n"
        response.write(headers)
        response.write(body_bytes)

    def handle_user_agent_endpoint(self, request, response):
        user_agent = request.get_header("user-agent")
        ua_bytes = user_agent.encode('utf-8')
        headers = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n"
        if request.client_accepts_gzip():
            headers += "Content-Encoding: gzip\r\n"
        headers += f"Content-Length: {len(ua_bytes)}\r\n\r\n"
        response.write(headers)
        response.write(ua_bytes)

    def handle_files_endpoint(self, request, response):
        if not self.files_directory:
            response.write("HTTP/1.1 500 Internal Server Error\r\n\r\n")
            return
        
        filename = request.get_path()[7:]  # Strip "/files/"
        file_path = os.path.join(self.files_directory, filename)
        
        if request.get_method() == "GET":
            self.handle_get_request(file_path, response)
        elif request.get_method() == "POST":
            self.handle_post_request(file_path, request, response)
        else:
            response.write("HTTP/1.1 405 Method Not Allowed\r\n\r\n")

    def handle_get_request(self, file_path, response):
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            response.write(f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(file_bytes)}\r\n\r\n")
            response.write(file_bytes)
        else:
            response.write("HTTP/1.1 404 Not Found\r\n\r\n")

    def handle_post_request(self, file_path, request, response):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(request.get_body())
            response.write("HTTP/1.1 201 Created\r\n\r\n")
        except IOError:
            response.write("HTTP/1.1 500 Internal Server Error\r\n\r\n")
