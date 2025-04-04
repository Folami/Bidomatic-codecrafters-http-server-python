import socket
import sys
import os
import threading


class HttpServer:
    def __init__(self, args):
        self.args = args
        self.port = 4221
        self.directory = None
        self.server_socket = socket.create_server(("localhost", self.port), reuse_port=True)


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
            print("Accepted connection from", addr)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()


    def handle_client(self, client_socket):
        try:
            method, path, headers, body = self.read_http_request(client_socket)
            
            # Add /user-agent endpoint handling
            if path == "/user-agent":
                user_agent = headers.get("user-agent", "")
                body_bytes = user_agent.encode('utf-8')
                response = "HTTP/1.1 200 OK\r\n"
                response += "Content-Type: text/plain\r\n"
                response += f"Content-Length: {len(body_bytes)}\r\n\r\n"
                client_socket.sendall(response.encode('utf-8') + body_bytes)
                return
            
            # Add root path handling at the start
            if path == "/" or path == "/index.html":
                response = "HTTP/1.1 200 OK\r\n\r\n"
                client_socket.sendall(response.encode('utf-8'))
                return
                
            if path.startswith("/echo/"):
                # Extract the text to echo from the path
                echo_text = path[len("/echo/"):]
                # Check if client accepts gzip encoding
                accept_encoding = headers.get("accept-encoding", "")
                
                if "gzip" in accept_encoding.lower():
                    # Use gzip compression
                    import gzip
                    content = gzip.compress(echo_text.encode('utf-8'))
                    response = "HTTP/1.1 200 OK\r\n"
                    response += "Content-Type: text/plain\r\n"
                    response += "Content-Encoding: gzip\r\n"
                    response += f"Content-Length: {len(content)}\r\n\r\n"
                    client_socket.sendall(response.encode('utf-8') + content)
                else:
                    # No compression
                    content = echo_text.encode('utf-8')
                    response = "HTTP/1.1 200 OK\r\n"
                    response += "Content-Type: text/plain\r\n"
                    response += f"Content-Length: {len(content)}\r\n\r\n"
                    client_socket.sendall(response.encode('utf-8') + content)
                return
            
            if path.startswith("/files/"):
                filename = path[len("/files/"):]
                full_path = os.path.join(self.directory, filename) if self.directory else None
                
                if method.upper() == "POST":
                    if not full_path:
                        response = "HTTP/1.1 404 Not Found\r\n\r\n"
                    else:
                        try:
                            # Write the request body to file
                            with open(full_path, 'wb') as f:
                                f.write(body.encode('utf-8'))
                            response = "HTTP/1.1 201 Created\r\n\r\n"
                        except Exception as e:
                            print(f"Error writing file: {e}")
                            response = "HTTP/1.1 500 Internal Server Error\r\n\r\n"
                    client_socket.sendall(response.encode('utf-8'))
                    return
                
                elif method.upper() == "GET":
                    if full_path and os.path.isfile(full_path):
                        try:
                            with open(full_path, "rb") as f:
                                content = f.read()
                            response = "HTTP/1.1 200 OK\r\n"
                            response += "Content-Type: application/octet-stream\r\n"
                            response += f"Content-Length: {len(content)}\r\n\r\n"
                            client_socket.sendall(response.encode('utf-8') + content)
                        except Exception as e:
                            print(f"Error reading file: {e}")
                            response = "HTTP/1.1 500 Internal Server Error\r\n\r\n"
                            client_socket.sendall(response.encode('utf-8'))
                    else:
                        response = "HTTP/1.1 404 Not Found\r\n\r\n"
                        client_socket.sendall(response.encode('utf-8'))
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"
                client_socket.sendall(response.encode('utf-8'))
        except Exception as err:
            print(f"Error handling request: {err}")
            try:
                response = "HTTP/1.1 500 Internal Server Error\r\n\r\n"
                client_socket.sendall(response.encode('utf-8'))
            except:
                pass
        finally:
            client_socket.close()

    def read_http_request(self, client_socket):
        request = b""
        while b"\r\n\r\n" not in request:
            chunk = client_socket.recv(1024)
            if not chunk:
                break
            request += chunk

        # Split headers from body
        headers_raw, _, initial_body = request.partition(b"\r\n\r\n")
        headers_text = headers_raw.decode('utf-8')
        
        # Parse request line and headers
        lines = headers_text.split("\r\n")
        if not lines:
            raise Exception("Empty request")
            
        method, path, _ = lines[0].split(" ")
        
        # Parse headers into dictionary
        headers = {}
        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()

        # Read remaining body based on Content-Length
        body = initial_body
        if "content-length" in headers:
            content_length = int(headers["content-length"])
            while len(body) < content_length:
                chunk = client_socket.recv(content_length - len(body))
                if not chunk:
                    break
                body += chunk

        return method, path, headers, body.decode('utf-8')
