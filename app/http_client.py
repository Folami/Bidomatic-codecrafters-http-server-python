import socket
import sys
from io import BytesIO
from app.http_request import HttpRequest
from app.http_response import HttpResponse


class HttpClient:
    def __init__(self, socket, server):
        self.socket = socket
        self.server = server

    def run(self):
        try:
            request = HttpRequest.read_request(self.socket)
            if not request:
                return
            
            response = HttpResponse()
            self.server.process_request(request, response)
            self.socket.sendall(response.getBytes())
        except Exception as e:
            print(f"Error in HttpClient: {e}")
        finally:
            self.socket.close()

