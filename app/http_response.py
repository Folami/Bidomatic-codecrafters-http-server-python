from io import BytesIO


class HttpResponse:
    def __init__(self):
        self.buffer = BytesIO()

    def write(self, data):
        if isinstance(data, str):
            self.buffer.write(data.encode('utf-8'))
        else:
            self.buffer.write(data)

    def get_bytes(self):
        return self.buffer.getvalue()