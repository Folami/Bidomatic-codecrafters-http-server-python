import socket
import sys
import os
import threading
import gzip
from io import BytesIO


class HttpServer:
    def __init__(self, args):
        self.args = args
        self.port = 4221
        self.directory = None
        if "--directory" in args:
            idx = args.index("--directory") + 1
            if idx < len(args):
                self.directory = args[idx]
                if not os.path.isdir(self.directory):
                    print("Error: Provided directory does not exist.")
                    sys.exit(1)
            else:
                print("Error: --directory flag provided without a path.")
                sys.exit(1)
        self.server_socket = socket.create_server(("localhost", self.port), reuse_port=True)

    def start(self):
        print("Server listening on port:", self.port)
        while True:
            client_socket, addr = self.server_socket.accept()
            print("Accepted connection from", addr)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        try:
            method, path, headers, body = self.read_http_request(client_socket)
            # Process /files endpoint for POST requests.
            if path.startswith("/files/"):
                filename = path[len("/files/"):]
                full_path = os.path.join(self.directory, filename) if self.directory else None
                if method.upper() == "POST":
                    try:
                        with open(full_path, "w", encoding="utf-8") as f:
                            f.write(body)
                        response = "HTTP/1.1 201 Created\r\n\r\n"
                    except Exception as e:
                        print("Error writing file:", e)
                        response = "HTTP/1.1 500 Internal Server Error\r\n\r\n"
                elif method.upper() == "GET":
                    if full_path and os.path.isfile(full_path):
                        try:
                            with open(full_path, "rb") as f:
                                file_bytes = f.read()
                            response_headers  = "HTTP/1.1 200 OK\r\n"
                            response_headers += "Content-Type: application/octet-stream\r\n"
                            response_headers += "Content-Length: " + str(len(file_bytes)) + "\r\n\r\n"
                            client_socket.sendall(response_headers.encode("utf-8") + file_bytes)
                            client_socket.close()
                            return
                        except Exception as e:
                            print("Error reading file:", e)
                            response = "HTTP/1.1 500 Internal Server Error\r\n\r\n"
                    else:
                        response = "HTTP/1.1 404 Not Found\r\n\r\n"
                else:
                    response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"
            elif path.startswith("/echo/"):
                echo_body = path[len("/echo/"):]
                accept_encoding = headers.get("accept-encoding", "")
                if "gzip" in accept_encoding.lower():
                    import gzip
                    compressed_body = gzip.compress(echo_body.encode("utf-8"))
                    response_header  = "HTTP/1.1 200 OK\r\n"
                    response_header += "Content-Type: text/plain\r\n"
                    response_header += "Content-Encoding: gzip\r\n"
                    response_header += "Content-Length: " + str(len(compressed_body)) + "\r\n"
                    response_header += "\r\n"
                    client_socket.sendall(response_header.encode("utf-8") + compressed_body)
                else:
                    body_bytes = echo_body.encode("utf-8")
                    response_header  = "HTTP/1.1 200 OK\r\n"
                    response_header += "Content-Type: text/plain\r\n"
                    response_header += "Content-Length: " + str(len(body_bytes)) + "\r\n"
                    response_header += "\r\n"
                    client_socket.sendall(response_header.encode("utf-8") + body_bytes)
                client_socket.close()
                return
            elif path == "/user-agent":
                # NEW: Handle /user-agent endpoint.
                ua = headers.get("user-agent", "")
                body_bytes = ua.encode("utf-8")
                response_header  = "HTTP/1.1 200 OK\r\n"
                response_header += "Content-Type: text/plain\r\n"
                response_header += "Content-Length: " + str(len(body_bytes)) + "\r\n"
                response_header += "\r\n"
                client_socket.sendall(response_header.encode("utf-8") + body_bytes)
            elif path == "/" or path == "/index.html":
                response = "HTTP/1.1 200 OK\r\n\r\n"
                client_socket.sendall(response.encode("utf-8"))
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"
                client_socket.sendall(response.encode("utf-8"))
        except Exception as err:
            print("Error handling request:", err)
        finally:
            client_socket.close()

    def read_http_request(self, client_socket):
        buffer = b""
        # Read until headers are complete ("\r\n\r\n" found)
        while b"\r\n\r\n" not in buffer:
            data = client_socket.recv(1024)
            if not data:
                break
            buffer += data
        header_part, sep, remainder = buffer.partition(b"\r\n\r\n")
        header_text = header_part.decode("utf-8", errors="replace")
        lines = header_text.split("\r\n")
        if not lines:
            raise Exception("Invalid HTTP request")
        # Parse the request line.
        request_line = lines[0]
        parts = request_line.split(" ")
        if len(parts) < 3:
            raise Exception("Invalid request line")
        method = parts[0].strip()
        path = parts[1].strip()
        # Parse headers into a dict.
        headers = {}
        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()
        # Get declared content-length (if any)
        content_length = 0
        if "content-length" in headers:
            try:
                content_length = int(headers["content-length"])
            except ValueError:
                content_length = 0
        body = remainder
        # If the already-read body is shorter than content_length, read the rest.
        while len(body) < content_length:
            data = client_socket.recv(content_length - len(body))
            if not data:
                break
            body += data
        return method, path, headers, body.decode("utf-8", errors="replace")
