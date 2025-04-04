import sys
from app.http_server import HttpServer



def main():
    server = HttpServer(sys.argv)
    server.start()

if __name__ == "__main__":
    main()