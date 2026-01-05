import socket
import threading
from .shaper import TrafficShaper
from ..shared.protocol import ProtocolHandler
import os
import selectors


class Selector:
    def __init__(self, sel, sock, rsignaler, wsignaler):
        self.sel = sel
        self.sock = sock
        self.rsignaler = rsignaler
        self.wsignaler = wsignaler

    def signal(self):
        os.write(self.wsignaler, b'x')


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
            self.client_sock = self.ssl_context.wrap_socket(self.client_sock, server_side=True)

            # 2. Identify target using the shared protocol
            request_data = self.client_sock.recv(1024)
            target = ProtocolHandler.parse_request(request_data)

            if not target:
                self.client_sock.sendall(b"ERROR\n")
                return

            # 3. Connect to original destination
            try:
                self.target_sock = socket.create_connection(target, timeout=10.0)
                self.client_sock.sendall(b"OK\n")
            except socket.error:
                self.client_sock.sendall(b"ERROR\n")  # Notify client of failure
                return

            self.client_sel, self.target_sel = self._create_selectors(self.client_sock, self.target_sock)

            # 4. Multithreaded Bidirectional Relay
            # Thread A: Client -> Target (Upload)
            up_thread = threading.Thread(target=self._relay, args=(self.client_sel, self.target_sock, False))
            # Thread B: Target -> Client (Download with Obfuscation)
            down_thread = threading.Thread(target=self._relay, args=(self.target_sel, self.client_sock, True))

            up_thread.start()
            down_thread.start()

            # Wait for both threads to finish
            up_thread.join()
            down_thread.join()

        except Exception as e:
            print(f"[-] Session Error: {e}")
        finally:
            self._cleanup()

    def _relay(self, sel: Selector, destination, use_shaper):
        """Generic relay function for one-way traffic."""
        try:
            while self.running:
                events = sel.sel.select()
                for key, mask in events:
                    if key.data == "SOCKET":
                        data = sel.sock.recv(4096)
                        if not data:
                            self._stop()
                        self._send(destination, data, use_shaper)
        except Exception:
            pass
        finally:
            self._stop()

    def _send(self, destination, data, use_shaper):
        if use_shaper:
            # Apply random delays and segmentation
            self.shaper.send_obfuscated(destination, data)
        else:
            destination.sendall(data)

    def _stop(self):
        self.running = False
        os.write(self.client_sel.wsignaler, b'x')

    def _cleanup(self):
        """Ensures both connections are closed on error or completion."""
        self.target_sock.close()
        self.client_sock.close()
        os.close(self.client_sel.rsignaler)
        os.close(self.client_sel.wsignaler)

    @classmethod
    def _create_selectors(cls, sock_client, sock_target):
        rsignaler, wsignaler = os.pipe()

        sel_client = selectors.DefaultSelector()
        sel_client.register(sock_client, selectors.EVENT_READ, data="SOCKET")
        sel_client.register(rsignaler, selectors.EVENT_READ, data="ABORT")

        sel_target = selectors.DefaultSelector()
        sel_target.register(sock_target, selectors.EVENT_READ, data="SOCKET")
        sel_target.register(rsignaler, selectors.EVENT_READ, data="ABORT")

        return Selector(sel_client, sock_client, rsignaler, wsignaler), \
            Selector(sel_target, sock_target, rsignaler, wsignaler)
