import pytest
from unittest.mock import MagicMock, patch
from src.minitor.socket import MiniTorSocket


@pytest.fixture
def mock_tor_socket():
    # Patching ssl and socket to avoid real network calls
    with patch('socket.socket'), patch('ssl.create_default_context'):
        client = MiniTorSocket("proxy.local", 8080, "path/to/cert.crt")
        yield client


def test_socket_initialization(mock_tor_socket):
    """Test if internal state is correctly initialized."""
    assert mock_tor_socket.node_addr == ("proxy.local", 8080)
    assert mock_tor_socket.sock is None


def test_connect_success(mock_tor_socket):
    """Test successful tunnel establishment on 'OK' response."""
    mock_ssl_sock = MagicMock()
    mock_ssl_sock.recv.return_value = b"OK\n"
    mock_tor_socket.context.wrap_socket.return_value = mock_ssl_sock

    mock_tor_socket.connect("target.com", 80)

    assert mock_tor_socket.sock == mock_ssl_sock
    mock_ssl_sock.sendall.assert_called()  # Should send CONNECT request


def test_connect_node_error(mock_tor_socket):
    """Verify ConnectionError is raised when node returns 'ERROR'."""
    mock_ssl_sock = MagicMock()
    mock_ssl_sock.recv.return_value = b"ERROR\n"
    mock_tor_socket.context.wrap_socket.return_value = mock_ssl_sock

    with pytest.raises(ConnectionError, match="Node could not reach target"):
        mock_tor_socket.connect("bad-target.com", 80)

    assert mock_tor_socket.sock is None  # Should be closed/reset


def test_send_unconnected_raises_error(mock_tor_socket):
    """Ensure send() fails if connect() wasn't called."""
    with pytest.raises(ConnectionError, match="Not connected"):
        mock_tor_socket.send(b"data")
