import socket  # noqa: F401

def main():
    print("Logs from your program will appear here!")
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    
    while True:
        conn, addr = server_socket.accept()
        print("Accepted connection from", addr)
        
        # Read the request (up to 1024 bytes).
        request = conn.recv(1024)
        request_text = request.decode("utf-8")
        
        # Split the request into lines (using CRLF as the separator).
        request_lines = request_text.split("\r\n")
        
        # Default the path to empty if something goes wrong.
        path = ""
        if request_lines:
            # The first line should be something like "GET /index.html HTTP/1.1"
            request_line = request_lines[0]
            parts = request_line.split(" ")
            if len(parts) >= 2:
                # Strip any extraneous whitespace.
                path = parts[1].strip()
            else:
                path = ""
        else:
            path = ""
        
        print("Requested path:", repr(path))
        
        # Handle endpoints.
        if path == "/" or path == "/index.html":
            response = "HTTP/1.1 200 OK\r\n\r\n"
        elif path.startswith("/echo/"):
            # Extract the string following "/echo/"
            echo_body = path[len("/echo/"):]
            # Determine byte length of body (assumes UTF-8 encoding).
            content_length = len(echo_body.encode("utf-8"))
            # Build response with required headers.
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type: text/plain\r\n"
            response += "Content-Length: " + str(content_length) + "\r\n"
            response += "\r\n"
            response += echo_body
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
            
        conn.sendall(response.encode("utf-8"))
        conn.close()

if __name__ == "__main__":
    main()