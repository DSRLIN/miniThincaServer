from __future__ import annotations

import argparse
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from mini_thinca_lib import MiniThinca


def guess_lan_ip() -> str:
    host = socket.gethostname()
    for info in socket.getaddrinfo(host, None, family=socket.AF_INET):
        ip = info[4][0]
        if ip.startswith("192."):
            return ip
    return "127.0.0.1"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", nargs="?", default=None)
    parser.add_argument("--port", type=int, default=80)
    args = parser.parse_args()

    ip = args.ip or guess_lan_ip()
    app = MiniThinca(ip)

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0"))
            payload = self.rfile.read(length) if length > 0 else b""
            code, headers, body = app.dispatch(self.path, payload)
            self.send_response(code)
            for k, v in headers.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            code, headers, body = app.dispatch(self.path, b"")
            self.send_response(code)
            for k, v in headers.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    print(f"miniThinca Server online at http://0.0.0.0:{args.port} (ip={ip})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down...")
        server.server_close()


if __name__ == "__main__":
    main()
