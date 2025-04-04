import socket  # noqa: F401


def main():
    print("Logs from your program will appear here!")

    # Create TCP Server that's bound to and listens on port 4221.
    # Set reuse_port to true for testing
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    
    # Respond to HTTP request with 200 response.
    while True:
        client_socket, addr = server_socket.accept()
        print("Accepted connection from", addr)
        response = "HTTP/1.1 200 OK\r\n\r\n"
        client_socket.sendall(response.encode("utf-8"))
        client_socket.close()



import socket  # noqa: F401

def main():
    print("Logs from your program will appear here!")
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    
    while True:
        client_socket, addr = server_socket.accept()
        print("Accepted connection from", addr)
        
        # Read the request (up to 1024 bytes).
        request = client_socket.recv(1024)
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
        
        # Return 200 OK if the path is "/" or "/index.html"; 404 otherwise.
        if path == "/" or path == "/index.html":
            response = "HTTP/1.1 200 OK\r\n\r\n"
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
            
        client_socket.sendall(response.encode("utf-8"))
        client_socket.close()


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
        elif path == "/user-agent":
            user_agent = ""
            # Iterate over header lines (everything after the request line)
            for line in request_lines[1:]:
                # An empty line marks end of headers.
                if line == "":
                    break
                # Look for the User-Agent header (case-insensitive).
                if line.lower().startswith("user-agent:"):
                    # Split on ":", then strip whitespace.
                    user_agent = line.split(":", 1)[1].strip()
                    break
            content_length = len(user_agent.encode("utf-8"))
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type: text/plain\r\n"
            response += "Content-Length: " + str(content_length) + "\r\n"
            response += "\r\n"
            response += user_agent
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
            
        conn.sendall(response.encode("utf-8"))
        conn.close()


import socket  # noqa: F401
import threading

def handle_client(conn, addr):
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
    elif path == "/user-agent":
        user_agent = ""
        # Iterate over header lines (everything after the request line)
        for line in request_lines[1:]:
            # An empty line marks end of headers.
            if line == "":
                break
            # Look for the User-Agent header (case-insensitive).
            if line.lower().startswith("user-agent:"):
                # Split on ":", then strip whitespace.
                user_agent = line.split(":", 1)[1].strip()
                break
        content_length = len(user_agent.encode("utf-8"))
        response = "HTTP/1.1 200 OK\r\n"
        response += "Content-Type: text/plain\r\n"
        response += "Content-Length: " + str(content_length) + "\r\n"
        response += "\r\n"
        response += user_agent
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
    
    conn.sendall(response.encode("utf-8"))
    conn.close()

def main():
    print("Logs from your program will appear here!")
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    
    while True:
        conn, addr = server_socket.accept()
        # Create a new thread to handle the connection.
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()



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
        conn.sendall(response.encode("utf-8"))
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
        conn.sendall(response.encode("utf-8"))
    elif path == "/user-agent":
        user_agent = ""
        # Iterate over header lines (everything after the request line)
        for line in request_lines[1:]:
            # An empty line marks end of headers.
            if line == "":
                break
            # Look for the User-Agent header (case-insensitive).
            if line.lower().startswith("user-agent:"):
                # Split on ":", then strip whitespace.
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
            # Extract the filename following "/files/"
            filename = path[len("/files/"):]
            full_path = os.path.join(files_dir, filename)
            if os.path.isfile(full_path):
                try:
                    with open(full_path, "rb") as f:
                        file_bytes = f.read()
                    content_length = len(file_bytes)
                    response_header = "HTTP/1.1 200 OK\r\n"
                    response_header += "Content-Type: application/octet-stream\r\n"
                    response_header += "Content-Length: " + str(content_length) + "\r\n"
                    response_header += "\r\n"
                    # Send headers and then the file content.
                    conn.sendall(response_header.encode("utf-8") + file_bytes)
                except Exception as e:
                    response = "HTTP/1.1 500 Internal Server Error\r\n\r\n"
                    conn.sendall(response.encode("utf-8"))
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"
                conn.sendall(response.encode("utf-8"))
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
        conn.sendall(response.encode("utf-8"))
    
    conn.close()

def main():
    global files_dir
    print("Logs from your program will appear here!")
    
    # Parse command-line arguments to get the --directory flag.
    # Example usage: ./your_program.sh --directory /tmp/
    if "--directory" in sys.argv:
        try:
            dir_index = sys.argv.index("--directory") + 1
            files_dir = sys.argv[dir_index]
            # Ensure the provided directory exists.
            if not os.path.isdir(files_dir):
                print("Error: Provided directory does not exist.")
                sys.exit(1)
        except IndexError:
            print("Error: --directory flag provided without a path.")
            sys.exit(1)
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    
    while True:
        conn, addr = server_socket.accept()
        # Create a new thread to handle the connection.
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()

if __name__ == "__main__":
    main()