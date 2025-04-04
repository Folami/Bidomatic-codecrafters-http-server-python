import os
import sys
import socket
import threading
from io import BytesIO
from app.http_client import HttpClient


class HttpServer:
    def __init__(self, args, port):
        self.args = args
        self.port = port
        self.directory = None
        self.server_socket = socket.create_server(("localhost", self.port), reuse_port=True)
        self.parse_command_line_args()


    def parse_command_line_args(self):
        # Parse for --directory flag.
        if "--directory" in self.args:
            idx = self.args.index("--directory") + 1
            if idx < len(self.args):
                self.directory = self.args[idx]
                if not os.path.isdir(self.directory):
                    print("Error: Provided directory does not exist.")
                    sys.exit(1)
            else:
                print("Error: --directory flag provided without a path.")
                sys.exit(1)
        # Check for other flags if needed.
        if "--port" in self.args:
            idx = self.args.index("--port") + 1
            if idx < len(self.args):
                try:
                    self.port = int(self.args[idx])
                except ValueError:
                    print("Error: Invalid port number.")
                    sys.exit(1)
            else:
                print("Error: --port flag provided without a port number.")
                sys.exit(1)
        # Check for other flags if needed.
        if "--help" in self.args:
            print("Usage: python http_server.py [--directory <path>] [--port <port>]")
            sys.exit(0)
        # Check for other flags if needed.
        if "--version" in self.args:
            print("HTTP Server version 1.0")
            sys.exit(0)
        # Check for other flags if needed.
        if "--verbose" in self.args:
            print("Verbose mode enabled.")
            # Add verbose handling here if needed.
        # Check for other flags if needed.
        if "--quiet" in self.args:
            print("Quiet mode enabled.")
            # Add quiet handling here if needed.
        # Check for other flags if needed.
        if "--debug" in self.args:
            print("Debug mode enabled.")
            # Add debug handling here if needed.


    def start(self):
        print("Server listening on port:", self.port)
        while True:
            client_socket, addr = self.server_socket.accept()
            print("Accepted connection from ", addr)
            threading.Thread(target=HttpClient, args=(client_socket,)).start()


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
        # Strip off the /echo/ prefix
        echo_body = request.get_path()[6:]  # Python's string slicing
        body_bytes = echo_body.encode('utf-8')
        headers = "HTTP/1.1 200 OK\r\n"
        headers += "Content-Type: text/plain\r\n"
        if request.client_accepts_gzip():
            headers += "Content-Encoding: gzip\r\n"
        headers += f"Content-Length: {len(body_bytes)}\r\n\r\n"
        response.write(headers)
        response.write(body_bytes)

    def handle_user_agent_endpoint(self, request, response):
        user_agent = request.get_header("user-agent")
        ua_bytes = user_agent.encode('utf-8')
        headers = "HTTP/1.1 200 OK\r\n"
        headers += "Content-Type: text/plain\r\n"
        if request.client_accepts_gzip():
            headers += "Content-Encoding: gzip\r\n"
        headers += f"Content-Length: {len(ua_bytes)}\r\n\r\n"
        response.write(headers)
        response.write(ua_bytes)

    def handle_files_endpoint(self, request, response):
        if not self.files_directory:
            response.write("HTTP/1.1 500 Internal Server Error\r\n\r\n")
            return
        
        filename = request.get_path()[len("/files/"):]
        file_path = os.path.join(self.files_directory, filename)
        if request.method == "GET":
            self.handle_get_request(file_path, response)
        elif request.method == "POST":
            self.handle_post_request(file_path, request, response)
        else:
            response.write("HTTP/1.1 405 Method Not Allowed\r\n\r\n")

    def handle_get_request(self, file_path, response):
        if os.path.exists(file_path) and os.path.isfile(file_path):
            file_bytes = self.read_file_bytes(file_path)
            headers = "HTTP/1.1 200 OK\r\n"
            headers += "Content-Type: application/octet-stream\r\n"
            headers += f"Content-Length: {len(file_bytes)}\r\n\r\n"
            response.write(headers)
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

    def read_file_bytes(self, file_path):
        baos = BytesIO()
        with open(file_path, 'rb') as f:
            buffer = f.read(4096)
            while buffer:
                baos.write(buffer)
                buffer = f.read(4096)
        return baos.getvalue()

