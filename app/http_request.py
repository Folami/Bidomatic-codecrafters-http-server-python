

class HttpRequest:
    def __init__(self, method, path, request_lines):
        self.method = method
        self.path = path
        self.request_lines = request_lines
        self.body = ""

    def get_method(self):
        return self.method

    def get_path(self):
        return self.path

    def get_request_lines(self):
        return self.request_lines

    def get_body(self):
        return self.body

    def read_body(self, socket):
        content_length = 0
        for header in self.request_lines:
            if header.lower().startswith("content-length:"):
                try:
                    content_length = int(header.split(":", 1)[1].strip())
                except ValueError:
                    content_length = 0
                break
        
        if content_length > 0:
            self.body = socket.recv(content_length).decode('utf-8')

    @staticmethod
    def read_request(socket):
        buffer = b""
        while b"\r\n\r\n" not in buffer:
            data = socket.recv(1024)
            if not data:
                return None
            buffer += data
        
        request_str = buffer.decode('utf-8')
        if not request_str:
            return None
        
        lines = request_str.split("\r\n")
        if not lines or len(lines[0].split()) < 2:
            return None
        
        method, path = lines[0].split()[:2]
        return HttpRequest(method.upper(), path, lines)

    def get_header(self, name):
        lower_name = name.lower()
        for header in self.request_lines:
            if header.lower().startswith(lower_name + ":"):
                return header.split(":", 1)[1].strip()
        return ""

    def client_accepts_gzip(self):
        for header in self.request_lines:
            if header.lower().startswith("accept-encoding:"):
                encodings = header[len("accept-encoding:"):].strip().lower()
                return "gzip" in encodings
        return False