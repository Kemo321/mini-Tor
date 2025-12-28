import socket
import ssl


CERT_FILE = 'demo/certs/server.crt'
KEY_FILE = 'demo/certs/server.key'


def start_target_server(host='0.0.0.0', port=80):
    """
    Simple target server that logs the client IP to demonstrate anonymity.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ctx.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()

        print("="*50)
        print('[TARGET] TARGET SERVER STARTING...')
        print(f'[TARGET] Listening on {host}:{port}')
        print("="*50)

        while True:
            conn, addr = s.accept()
            with conn:
                print("[TARGET] ALERT: Incoming connection established!")
                print(f"[TARGET] SOURCE IP (REMOTE_ADDR): {addr[0]}")
                print(f"[TARGET] SOURCE PORT: {addr[1]}")
                with ctx.wrap_socket(conn, server_side=True) as sec_conn:
                    data = sec_conn.recv(2048)
                    if data:
                        decoded_data = data.decode('utf-8', errors='ignore')

                        print("[TARGET] Received Data Stream:")
                        print("-" * 40)
                        print(decoded_data.strip())
                        print("-" * 40)

                        response_body = "Hello from the Target Server! Your identity is hidden."
                        response = (
                            "HTTP/1.1 200 OK\r\n"
                            "Content-Type: text/plain\r\n"
                            f"Content-Length: {len(response_body)}\r\n"
                            "Server: mini-TOR-Mock-Server\r\n"
                            "Connection: close\r\n"
                            "\r\n"
                            f"{response_body}"
                        )
                        sec_conn.sendall(response.encode('utf-8'))
                        print("[TARGET] Response sent successfully.")
            print("[TARGET] Connection closed.")
            print("-" * 50)


if __name__ == "__main__":
    try:
        start_target_server()
    except KeyboardInterrupt:
        print("\n[*] Target Server stopping...")
