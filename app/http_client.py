import sys
from io import BytesIO
from app.http_request import HttpRequest
from app.http_response import HttpResponse


class HttpClient:
    def __init__(self, client_socket, server):
        self.client_socket = client_socket
        self.server = server

    def run(self):
        try:
            with self.client_socket:
                request = HttpRequest.read_request(self.client_socket)
                if not request:
                    print("Error reading request, connection closed prematurely.", file=sys.stderr)
                    return
                
                if request.get_method() == "POST" and request.get_path().startswith("/files/"):
                    request.read_body(self.client_socket)
                
                response = HttpResponse()
                print(f"Method: {request.get_method()}, Path: {request.get_path()}")
                self.server.process_request(request, response)
                self.client_socket.sendall(response.get_bytes())
        except IOError as e:
            print(f"Error handling client: {e}", file=sys.stderr)

