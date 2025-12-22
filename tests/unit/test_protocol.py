import pytest
from src.shared.protocol import ProtocolHandler


def test_protocol_generation():
    """Verify correct generation of CONNECT requests."""
    assert ProtocolHandler.create_connect_request("127.0.0.1", 80) == b"CONNECT 127.0.0.1:80\n"
    assert ProtocolHandler.create_connect_request("google.com", 443) == b"CONNECT google.com:443\n"


@pytest.mark.parametrize("data, expected", [
    (b"CONNECT localhost:8080\n", ("localhost", 8080)),
    (b"CONNECT 192.168.1.1:22\n", ("192.168.1.1", 22)),
    (b"  CONNECT  whitespace.com:80  \n", ("whitespace.com", 80)),  # Test trimming
])
def test_protocol_parsing_valid(data, expected):
    """Verify parsing of various valid connection strings."""
    assert ProtocolHandler.parse_request(data) == expected


@pytest.mark.parametrize("invalid_data", [
    b"GET / HTTP/1.1\n",           # Wrong command
    b"CONNECT host_only\n",        # Missing port
    b"CONNECT host:not_a_number\n",  # Invalid port type
    b"",                           # Empty data
    b"\xff\xfe\xfd",               # Non-utf8 data
])
def test_protocol_parsing_invalid(invalid_data):
    """Ensure malformed requests return None instead of crashing."""
    assert ProtocolHandler.parse_request(invalid_data) is None
