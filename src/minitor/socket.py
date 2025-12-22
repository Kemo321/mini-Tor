import socket
import ssl
from ..shared.protocol import ProtocolHandler


class MiniTorSocket:
    """
    Socket wrapper that automatically tunnels traffic through an intermediate node.
    Implements requirement: client connects to node, not directly to target.
    """

    def __init__(self, node_host: str, node_port: int, ca_file: str):
        self.node_addr = (node_host, node_port)
        # Requirement: Use TLS for the tunnel
        self.context = ssl.create_default_context(cafile=ca_file)
        self.sock = None

    def connect(self, target_host: str, target_port: int):
        """
        1. Establishes TCP connection with intermediate node.
        2. Wraps it in TLS.
        3. Sends CONNECT request to node.
        """
        # 1 & 2: TCP + TLS
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.node_addr)
        self.sock = self.context.wrap_socket(sock, server_hostname=self.node_addr[0])

        # 3: Send CONNECT request
        connect_request = ProtocolHandler.create_connect_request(target_host, target_port)
        self.sock.sendall(connect_request)

        response = self.sock.recv(1024).decode('utf-8').strip()
        if response == "OK":
            print(f"[CLIENT] Tunnel established to {target_host}:{target_port}")
        elif response == "ERROR":
            self.close()
            raise ConnectionError(f"Node could not reach target {target_host}:{target_port}")
        else:
            self.close()
            raise ConnectionError("Unexpected protocol response from Node ")

    def send(self, data: bytes):
        """Sends data through encrypted tunnel."""
        if not self.sock:
            raise ConnectionError("Not connected")
        self.sock.sendall(data)

    def recv(self, bufsize: int) -> bytes:
        """Receives data from tunnel."""
        if not self.sock:
            raise ConnectionError("Not connected")
        return self.sock.recv(bufsize)

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
