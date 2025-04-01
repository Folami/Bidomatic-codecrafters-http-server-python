import socket  # noqa: F401
import threading
import sys
import os

# Global variable to store the files directory.
files_dir = None

def handle_client(conn, addr):
    print("Accepted connection from", addr)
    
    # Read the request (up to 1024 bytes).
    request = conn.recv(1024)
    request_text = request.decode("utf-8")
    
    # Split the request into lines (using CRLF as the separator).
    request_lines = request_text.split("\r\n")
    
    # Default the method and path to empty if something goes wrong.
    method = ""
    path = ""
    if request_lines:
        # The request-line should be something like "GET /index.html HTTP/1.1" or "POST /files/foo HTTP/1.1"
        request_line = request_lines[0]
        parts = request_line.split(" ")
        if len(parts) >= 2:
            method = parts[0].strip().upper()
            path = parts[1].strip()
        else:
            method = ""
            path = ""
    else:
        method = ""
        path = ""
    
    print("Method:", method, "Path:", repr(path))
    
    # Process endpoints.
    if path == "/" or path == "/index.html":
        response = "HTTP/1.1 200 OK\r\n\r\n"
        conn.sendall(response.encode("utf-8"))
    
    elif path.startswith("/echo/"):
        # Extract the string following "/echo/"
        echo_body = path[len("/echo/"):]
        content_length = len(echo_body.encode("utf-8"))
        response = "HTTP/1.1 200 OK\r\n"
        response += "Content-Type: text/plain\r\n"
        response += "Content-Length: " + str(content_length) + "\r\n"
        response += "\r\n"
        response += echo_body
        conn.sendall(response.encode("utf-8"))
    
    elif path == "/user-agent":
        user_agent = ""
        # Iterate over header lines (everything after the request line)
        for line in request_lines[1:]:
            if line == "":  # End of headers
                break
            if line.lower().startswith("user-agent:"):
                user_agent = line.split(":", 1)[1].strip()
                break
        content_length = len(user_agent.encode("utf-8"))
        response = "HTTP/1.1 200 OK\r\n"
        response += "Content-Type: text/plain\r\n"
        response += "Content-Length: " + str(content_length) + "\r\n"
        response += "\r\n"
        response += user_agent
        conn.sendall(response.encode("utf-8"))
    
    elif path.startswith("/files/"):
        # Ensure that the files directory was provided.
        if files_dir is None:
            response = "HTTP/1.1 500 Internal Server Error\r\n\r\n"
            conn.sendall(response.encode("utf-8"))
        else:
            filename = path[len("/files/"):]
            full_path = os.path.join(files_dir, filename)
            if method == "GET":
                # Serve the file if it exists.
                if os.path.isfile(full_path):
                    try:
                        with open(full_path, "rb") as f:
                            file_bytes = f.read()
                        content_length = len(file_bytes)
                        response_header  = "HTTP/1.1 200 OK\r\n"
                        response_header += "Content-Type: application/octet-stream\r\n"
                        response_header += "Content-Length: " + str(content_length) + "\r\n"
                        response_header += "\r\n"
                        conn.sendall(response_header.encode("utf-8") + file_bytes)
                    except Exception as e:
                        response = "HTTP/1.1 500 Internal Server Error\r\n\r\n"
                        conn.sendall(response.encode("utf-8"))
                else:
                    response = "HTTP/1.1 404 Not Found\r\n\r\n"
                    conn.sendall(response.encode("utf-8"))
            elif method == "POST":
                # Retrieve Content-Length from the headers.
                content_length = 0
                for line in request_lines[1:]:
                    if line == "":
                        break
                    if line.lower().startswith("content-length:"):
                        try:
                            content_length = int(line.split(":", 1)[1].strip())
                        except ValueError:
                            content_length = 0
                        break
                # Find the end of the headers ("\r\n\r\n")
                header_end = request_text.find("\r\n\r\n")
                if header_end != -1:
                    header_end += 4  # Move past "\r\n\r\n"
                else:
                    header_end = len(request_text)
                # Read the request body.
                request_body = request_text[header_end:]
                # In case the initial recv didn't fetch full body, you could read further here (not implemented).
                # Ensure only the declared Content-Length is taken.
                request_body = request_body[:content_length]
                try:
                    with open(full_path, "wb") as f:
                        f.write(request_body.encode("utf-8"))
                    response = "HTTP/1.1 201 Created\r\n\r\n"
                except Exception as e:
                    response = "HTTP/1.1 500 Internal Server Error\r\n\r\n"
                conn.sendall(response.encode("utf-8"))
            else:
                # Unsupported method for /files endpoint.
                response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"
                conn.sendall(response.encode("utf-8"))
    
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
        conn.sendall(response.encode("utf-8"))
    
    conn.close()

def main():
    global files_dir
    print("Logs from your program will appear here!")
    
    # Parse command-line arguments to get the --directory flag.
    if "--directory" in sys.argv:
        try:
            dir_index = sys.argv.index("--directory") + 1
            files_dir = sys.argv[dir_index]
            if not os.path.isdir(files_dir):
                print("Error: Provided directory does not exist.")
                sys.exit(1)
        except IndexError:
            print("Error: --directory flag provided without a path.")
            sys.exit(1)
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    
    while True:
        conn, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()

if __name__ == "__main__":
    main()