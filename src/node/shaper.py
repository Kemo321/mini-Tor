import time
import random
import socket


class TrafficShaper:
    """
    Implements obfuscation to hinder statistical traffic analysis.
    Used by the node to relay traffic to the client.
    """

    def __init__(self, min_delay=0.05, max_delay=0.2, max_chunk=512):
        self.delay_range = (min_delay, max_delay)
        self.max_chunk = max_chunk

    def send_obfuscated(self, sock: socket.socket, data: bytes):
        """
        Segments the data and introduces delays before sending.
        """
        offset = 0
        while offset < len(data):
            # 1. Determine a random chunk size (Segmentation)
            chunk_size = random.randint(1, self.max_chunk)
            chunk = data[offset:offset + chunk_size]

            # 2. Introduce a pseudorandom delay
            time.sleep(random.uniform(*self.delay_range))

            # 3. Send the segment
            sock.sendall(chunk)
            offset += chunk_size
