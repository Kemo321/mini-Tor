import socket
import ssl
import threading
from .handler import ConnectionHandler


class ProxyServer:
    def __init__(self, host, port, cert_file, key_file):
        self.addr = (host, port)
        self.ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.ctx.load_cert_chain(certfile=cert_file, keyfile=key_file)

    def start_listening(self):
        """
        Endless loop accepting new connections.
        Node returns to listening after errors.
        """
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind(self.addr)
        server_sock.listen(5)
        print(f"[+] Node listening on {self.addr}")

        while True:
            try:
                client_sock, _ = server_sock.accept()
                handler = ConnectionHandler(client_sock, self.ctx)
                # Start handler in a new thread
                t = threading.Thread(target=handler.run)
                t.daemon = True
                t.start()
            except Exception as e:
                print(f"[!] Critical Accept Error: {e}")
