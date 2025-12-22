import socket


def start_target_server(host='0.0.0.0', port=80):
    """
    A simple server that logs the IP of the requester to prove anonymity.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"[*] Target Server listening on {host}:{port}...")

        while True:
            conn, addr = s.accept()
            with conn:
                # Log the requester's IP
                print(f"[!] CONNECTION RECEIVED FROM: {addr[0]}")

                data = conn.recv(1024)
                if data:
                    print(f"[*] Received data: {data.decode('utf-8', errors='ignore')}")
                    # Send a simple response
                    response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nHello from the Target Server! Your identity is hidden."
                    conn.sendall(response.encode('utf-8'))
                print("-" * 40)


if __name__ == "__main__":
    start_target_server()
