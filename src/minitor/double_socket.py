import ssl


class DoubleSocket:
    def __init__(self, proxy_sock, ctx, server_hostname, allow_self_signed: bool = False):
        self.sock = proxy_sock
        self._incoming = ssl.MemoryBIO()
        self._outgoing = ssl.MemoryBIO()
        # If requested, disable hostname checking and certificate verification on the provided context.
        # WARNING: This makes the TLS connection insecure and should only be used for local testing.
        if allow_self_signed:
            try:
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            except Exception:
                # If ctx doesn't have these attributes, ignore and proceed.
                pass
        self._obj = ctx.wrap_bio(self._incoming, self._outgoing, server_hostname=server_hostname)
        self._handshake()

    def _handshake(self):
        while True:
            try:
                self._obj.do_handshake()
                break
            except (ssl.SSLWantReadError, ssl.SSLWantWriteError):
                # If the SSL object wants to write, there may be data to send.
                data_to_send = self._outgoing.read()
                if data_to_send:
                    self.sock.sendall(data_to_send)
                # Try reading any response data from the underlying socket. If nothing is available,
                # sock.recv may block; in calling code the socket may be non-blocking or have a timeout.
                try:
                    response = self.sock.recv(4096)
                except BlockingIOError:
                    # No data available right now, continue looping.
                    continue
                if not response:
                    # Remote closed connection; write nothing and allow do_handshake to raise/read accordingly.
                    continue
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
