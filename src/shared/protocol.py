class ProtocolHandler:
    """
    Handles the control messages sent within the TLS tunnel to manage
    the connection setup between the client and the proxy node.
    """

    @staticmethod
    def create_connect_request(target_host: str, target_port: int) -> bytes:
        """Formats the initial request to the node."""
        return f"CONNECT {target_host}:{target_port}\n".encode('utf-8')

    @staticmethod
    def parse_request(data: bytes) -> tuple[str, int] | None:
        """Parses the 'CONNECT host:port' command on the node side."""
        try:
            line = data.decode('utf-8').strip()
            if line.startswith("CONNECT "):
                parts = line.split()[1].split(":")
                return parts[0], int(parts[1])
        except (UnicodeDecodeError, IndexError, ValueError):
            return None
        return None
