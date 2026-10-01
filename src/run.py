"""Local development server using Python's standard-library WSGI server."""

from wsgiref.simple_server import make_server

from app import application


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5000
    print(f"Calculator backend: http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    with make_server(host, port, application) as server:
        server.serve_forever()
