from sonofflan.config import DeviceConfig
from sonofflan.devices.powerplug import PowerPlug
from tests import get_and_wait


def test_create():
    before = get_and_wait()
    dev = PowerPlug(
        {
            "id": "1234",
            "type": "enhanced_plug",
            "address": "address",
            "port": 123,
            "encrypt": False,
            "data": {
                "switch": "on",
                "voltage": 220.00,
                "current": 5.00,
                "power": 1100.00,
            },
        },
        DeviceConfig(
            {
                "id": "1234",
                "name": "Device 1",
            }
        )
    )
    after = get_and_wait()

    assert dev.id == "1234"
    assert dev.name == "Device 1"
    assert dev.encrypt is False
    assert dev.key is None
    assert dev.url == "http://address:123"
    assert before < after
    assert dev.last_update > before  # type: ignore
    assert dev.last_update < after  # type: ignore
    assert dev.status is True
    assert dev.voltage == 220.00
    assert dev.current == 5.00
    assert dev.power == 1100.00


def test_update():
    before = get_and_wait()
    dev = PowerPlug(
        {
            "id": "1234",
            "type": "enhanced_plug",
            "address": "address",
            "port": 123,
            "encrypt": False,
            "data": {
                "switch": "on",
                "voltage": 220.00,
                "current": 5.00,
                "power": 1100.00,
            },
        },
        DeviceConfig(
            {
                "id": "1234",
                "name": "Device 1",
            }
        )
    )
    after = get_and_wait()

    assert before < after
    assert dev.last_update > before  # type: ignore
    assert dev.last_update < after  # type: ignore
    assert dev.status is True
    assert dev.voltage == 220.00
    assert dev.current == 5.00
    assert dev.power == 1100.00

    dev.update({
        "id": "1234",
        "type": "enhanced_plug",
        "address": "address",
        "port": 123,
        "encrypt": False,
        "data": {
            "switch": "off",
            "voltage": 225.10,
            "current": 2.10,
            "power": 427.71,
        },
    })
    after_update = get_and_wait()

    assert after < after_update
    assert dev.last_update > after  # type: ignore
    assert dev.last_update < after_update  # type: ignore
    assert dev.status is False
    assert dev.voltage == 225.10
    assert dev.current == 2.10
    assert dev.power == 427.71
