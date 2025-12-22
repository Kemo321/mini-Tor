"""
Entry point for the Proxy Node.
This script initializes the server-side of the mini-TOR system.
"""
from src.node.server import ProxyServer
import os


def main():
    LISTEN_HOST = '0.0.0.0'  # Listen on all interfaces within the container
    LISTEN_PORT = 8080

    # Paths to SSL certificates
    CERT_FILE = 'certs/node.crt'
    KEY_FILE = 'certs/node.key'

    if not os.path.exists(CERT_FILE):
        print(f"[-] Error: Certificate file not found at {CERT_FILE}")
        return

    print("--- mini-TOR Node Starting ---")
    print(f"[*] Initializing TLS tunnel listener on {LISTEN_HOST}:{LISTEN_PORT}")

    # Initialize the server
    node = ProxyServer(
        host=LISTEN_HOST,
        port=LISTEN_PORT,
        cert_file=CERT_FILE,
        key_file=KEY_FILE
    )

    try:
        node.start_listening()
    except KeyboardInterrupt:
        print("\n[*] Node shutting down gracefully...")


if __name__ == "__main__":
    main()
