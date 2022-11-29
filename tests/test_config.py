import pytest

from sonofflan.config import DeviceConfig, DevicesConfig


# Tests for DeviceConfig
def test_deviceconfig_invalid():
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
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


# Tests for DevicesConfig
def test_devicesconfig_invalid():
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        DevicesConfig("")


def test_devicesconfig_none():
    dc = DevicesConfig()
    assert dc.num_devices() == 0
    assert dc.device("1234") is None
    assert dc.device("5678") is None
    assert dc.device("ABCD") is None


def test_devicesconfig_dict():
    dc = DevicesConfig({
        "1234": {
            "name": "Device 1"
        },
        "5678": {
            "name": "Device 2"
        }
    })
    assert dc.num_devices() == 2

    dev1 = dc.device("1234")
    assert dev1 is not None
    assert dev1.id == "1234"
    assert dev1.name == "Device 1"
    assert dev1.key is None

    dev2 = dc.device("5678")
    assert dev2 is not None
    assert dev2.id == "5678"
    assert dev2.name == "Device 2"
    assert dev2.key is None

    assert dc.device("ABCD") is None


def test_devicesconfig_list():
    dc = DevicesConfig([
        {
            "id": "1234",
            "name": "Device 1"
        }, {
            "id": "5678",
            "name": "Device 2"
        }
    ])
    assert dc.num_devices() == 2

    dev1 = dc.device("1234")
    assert dev1 is not None
    assert dev1.id == "1234"
    assert dev1.name == "Device 1"
    assert dev1.key is None

    dev2 = dc.device("5678")
    assert dev2 is not None
    assert dev2.id == "5678"
    assert dev2.name == "Device 2"
    assert dev2.key is None

    assert dc.device("ABCD") is None
