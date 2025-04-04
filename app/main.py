import sys
from app.http_server import HttpServer



def main():
    default_port = 4221
    server = HttpServer(sys.argv, default_port)
    server.start()

if __name__ == "__main__":
    main()
