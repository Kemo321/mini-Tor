"""
Demonstration of the mini-TOR library.
This script shows that the server sees the Node's IP, not the Client's.
"""
from src.minitor.socket import MiniTorSocket
import ssl
from src.minitor.double_socket import DoubleSocket


def run_demo():
    # 1. Configuration for the Proxy Node
    NODE_HOST = 'proxy-node.local'
    NODE_PORT = 8080
    NODE_CERT = 'certs/node.crt'
    SERVER_CERT = 'demo/certs/server.crt'

    # 2. Target destination (The server we want to reach anonymously)
    TARGET_HOST = 'target-server.com'
    TARGET_PORT = 80

    print("[CLIENT] Initializing mini-TOR connection...")
    print(f"[CLIENT] Proxy Node: {NODE_HOST}:{NODE_PORT}")
    print(f"[CLIENT] Target: {TARGET_HOST}:{TARGET_PORT}")

    proxy_socket = MiniTorSocket(NODE_HOST, NODE_PORT, NODE_CERT)
    print("[CLIENT] MiniTorSocket created")

    try:
        # Step 1: Connect to the target via the proxy node
        print("[CLIENT] Connecting to target through proxy node...")
        proxy_socket.connect(TARGET_HOST, TARGET_PORT)
        print(f"[CLIENT] Connected to {TARGET_HOST} through {NODE_HOST}")

        ctx = ssl.create_default_context(cafile=SERVER_CERT)
        sock = DoubleSocket(proxy_socket.sock, ctx, TARGET_HOST)

        print("socket wrapped")

        # Step 2: Prepare a simple HTTP request
        http_request = (
            f"GET / HTTP/1.1\r\n"
            f"Host: {TARGET_HOST}\r\n"
            f"User-Agent: mini-TOR-Client\r\n"
            f"Connection: close\r\n\r\n"
        )
        print(f"[CLIENT] HTTP Request: {http_request}")

        # Step 3: Send the data through the "safe" socket
        print("[CLIENT] Sending HTTP request...")
        sock.send(http_request.encode('utf-8'))

        # Step 4: Receive response in chunks
        print("[CLIENT] Waiting for response...")
        full_response = b""
        sock.sock.settimeout(5)

        while True:
            chunk = sock.recv(4096)
            if not chunk:
                print("[CLIENT] Connection closed by remote host.")
                break
            full_response += chunk
            print(f"[CLIENT] ... received {len(chunk)} bytes")

        if full_response:
            print("\n[CLIENT] Final response received from target server:")
            print("-" * 30)
            print(full_response.decode('utf-8', errors='ignore'))
            print("-" * 30)
        else:
            print("[CLIENT] No data received.")

    finally:
        print("[CLIENT] Closing connection")
        proxy_socket.close()


if __name__ == "__main__":
    run_demo()
