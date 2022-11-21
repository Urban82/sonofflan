import pytest

from sonofflan.config import DeviceConfig


# Tests for DeviceConfig
def test_deviceconfig_invalid():
    with pytest.raises(TypeError):
        DeviceConfig("")

def test_deviceconfig_empty():
    with pytest.raises(ValueError):
        DeviceConfig({})

def test_deviceconfig_only_id():
    dc = DeviceConfig({"id": "1234"})
    assert dc.id == "1234"
    assert dc.name == "[1234]"
    assert dc.key is None

def test_deviceconfig_with_name():
    dc = DeviceConfig({"id": "1234", "name": "ABCD"})
    assert dc.id == "1234"
    assert dc.name == "ABCD"
    assert dc.key is None

def test_deviceconfig_with_key():
    dc = DeviceConfig({"id": "1234", "name": "ABCD", "key": "!£$%"})
    assert dc.id == "1234"
    assert dc.name == "ABCD"
    assert dc.key == "!£$%"
