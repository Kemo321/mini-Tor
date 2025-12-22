import pytest


def test_placeholder():
    with pytest.raises(ZeroDivisionError):
        1 / 0
