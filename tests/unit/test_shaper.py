import time
from unittest.mock import MagicMock
from src.node.shaper import TrafficShaper


def test_shaper_data_integrity():
    """Ensure data sent through the shaper is identical to original data."""
    mock_sock = MagicMock()
    shaper = TrafficShaper(min_delay=0, max_delay=0, max_chunk=10)
    original_data = b"Testing data integrity across multiple chunks"

    shaper.send_obfuscated(mock_sock, original_data)

    # Reconstruct segments from mock calls
    all_calls = mock_sock.sendall.call_args_list
    reconstructed = b"".join(call.args[0] for call in all_calls)

    assert reconstructed == original_data


def test_shaper_chunk_size_limits():
    """Verify that no segment exceeds the max_chunk size."""
    mock_sock = MagicMock()
    max_limit = 5
    shaper = TrafficShaper(min_delay=0, max_delay=0, max_chunk=max_limit)

    shaper.send_obfuscated(mock_sock, b"This is a relatively long string")

    for call in mock_sock.sendall.call_args_list:
        assert len(call.args[0]) <= max_limit


def test_shaper_timing_delay():
    """Verify that delays are actually being applied (probabilistic test)."""
    mock_sock = MagicMock()
    # High delay to ensure it's measurable
    shaper = TrafficShaper(min_delay=0.1, max_delay=0.1, max_chunk=10)
    data = b"TwoChunks"  # Will be split into at least 1 or 2

    start_time = time.time()
    shaper.send_obfuscated(mock_sock, data)
    duration = time.time() - start_time

    # Should take at least (number of chunks * min_delay)
    assert duration >= 0.1
