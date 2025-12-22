"""
Demonstration of the mini-TOR library.
This script shows that the server sees the Node's IP, not the Client's.
"""
from src.minitor.socket import MiniTorSocket


def run_demo():
    # 1. Configuration for the Proxy Node
    NODE_HOST = 'proxy-node.local'
    NODE_PORT = 8080
    CA_CERT = 'certs/node.crt'

    # 2. Target destination (The server we want to reach anonymously)
    TARGET_HOST = 'target-server.com'
    TARGET_PORT = 80

    print("[*] Initializing mini-TOR connection...")

    secure_socket = MiniTorSocket(NODE_HOST, NODE_PORT, CA_CERT)

    try:
        # Step 1: Connect to the target via the proxy node
        secure_socket.connect(TARGET_HOST, TARGET_PORT)
        print(f"[+] Connected to {TARGET_HOST} through {NODE_HOST}")

        # Step 2: Prepare a simple HTTP request
        http_request = (
            f"GET / HTTP/1.1\r\n"
            f"Host: {TARGET_HOST}\r\n"
            f"User-Agent: mini-TOR-Client\r\n"
            f"Connection: close\r\n\r\n"
        )

        # Step 3: Send the data through the "safe" socket
        secure_socket.send(http_request.encode('utf-8'))

        # Step 4: Receive response (This will be affected by random delays)
        response = secure_socket.recv(4096)
        print("\n[+] Response received from target server:")
        print("-" * 30)
        print(response.decode('utf-8', errors='ignore'))
        print("-" * 30)

    except Exception as e:
        print(f"[-] Demo failed: {e}")
    finally:
        secure_socket.close()


if __name__ == "__main__":
    run_demo()
