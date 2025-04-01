import socket  # noqa: F401

def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    
    while True:
        conn, addr = server_socket.accept()
        print("Accepted connection from", addr)
        response = "HTTP/1.1 200 OK\r\n\r\n"
        conn.sendall(response.encode("utf-8"))
        conn.close()

if __name__ == "__main__":
    main()



import socket  # noqa: F401

def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    
    while True:
        conn, addr = server_socket.accept()
        print("Accepted connection from", addr)
        
        # Read up to 1024 bytes from the request
        request = conn.recv(1024)
        request_text = request.decode("utf-8")
        # Split the request into lines using CRLF as delimiter
        request_lines = request_text.split("\r\n")
        
        if request_lines:
            # The first line is the request-line: e.g. "GET /index.html HTTP/1.1"
            request_line = request_lines[0]
            parts = request_line.split(" ")
            # Ensure we have at least 2 parts (method and path)
            if len(parts) >= 2:
                path = parts[1]
            else:
                path = ""
        else:
            path = ""
        
        print("Requested path:", path)
        
        # Return 200 OK if the path is "/index.html", 404 Not Found otherwise.
        if path == "/index.html":
            response = "HTTP/1.1 200 OK\r\n\r\n"
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
        
        conn.sendall(response.encode("utf-8"))
        conn.close()
        
if __name__ == "__main__":
    main()