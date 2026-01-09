import ssl


class DoubleSocket:
    def __init__(self, proxy_sock, ctx, server_hostname):
        self.sock = proxy_sock
        self._incoming = ssl.MemoryBIO()
        self._outgoing = ssl.MemoryBIO()
        self._obj = ctx.wrap_bio(self._incoming, self._outgoing, server_hostname=server_hostname)
        self._handshake()

    def _handshake(self):
        while True:
            try:
                self._obj.do_handshake()
                break
            except ssl.SSLWantReadError:
                data_to_send = self._outgoing.read()
                if data_to_send:
                    self.sock.sendall(data_to_send)
                response = self.sock.recv(4096)
                self._incoming.write(response)

    def send(self, data):
        self._obj.write(data)
        encrypted = self._outgoing.read()
        self.sock.send(encrypted)

    def recv(self, n):
        while True:
            try:
                encrypted = self.sock.recv(n)
                if not encrypted:
                    return encrypted
                self._incoming.write(encrypted)
                return self._obj.read()
            except ssl.SSLWantReadError:
                pass
