import socket
import threading
from .shaper import TrafficShaper
from ..shared.protocol import ProtocolHandler


class ConnectionHandler:
    """
    Manages the lifecycle of a single anonymous session using multithreading.
    """
    def __init__(self, client_sock, ssl_context):
        self.client_sock = client_sock
        self.ssl_context = ssl_context
        self.target_sock = None
        self.shaper = TrafficShaper()
        self.running = True

    def run(self):
        try:
            # 1. Wrap client in TLS
            secure_client = self.ssl_context.wrap_socket(self.client_sock, server_side=True)

            # 2. Identify target using the shared protocol
            request_data = secure_client.recv(1024)
            target = ProtocolHandler.parse_request(request_data)

            if not target:
                secure_client.sendall(b"ERROR\n")
                return

            # 3. Connect to original destination
            try:
                self.target_sock = socket.create_connection(target, timeout=10.0)
                secure_client.sendall(b"OK\n")
            except socket.error:
                secure_client.sendall(b"ERROR\n")  # Notify client of failure
                return

            # 4. Multithreaded Bidirectional Relay
            # Thread A: Client -> Target (Upload)
            up_thread = threading.Thread(target=self._relay, args=(secure_client, self.target_sock, False))
            # Thread B: Target -> Client (Download with Obfuscation)
            down_thread = threading.Thread(target=self._relay, args=(self.target_sock, secure_client, True))

            up_thread.start()
            down_thread.start()

            # Wait for both threads to finish
            up_thread.join()
            down_thread.join()

        except Exception as e:
            print(f"[-] Session Error: {e}")
        finally:
            self._cleanup()

    def _relay(self, source, destination, use_shaper):
        """Generic relay function for one-way traffic."""
        try:
            while self.running:
                data = source.recv(4096)
                if not data:
                    break

                if use_shaper:
                    # Apply random delays and segmentation
                    self.shaper.send_obfuscated(destination, data)
                else:
                    destination.sendall(data)
        except Exception:
            pass
        finally:
            self.running = False  # Signal the other thread to stop

    def _cleanup(self):
        """Ensures both connections are closed on error or completion."""
        if self.target_sock:
            self.target_sock.close()
        try:
            self.client_sock.close()
        except Exception:
            pass
