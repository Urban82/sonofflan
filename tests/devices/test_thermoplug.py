from sonofflan.config import DeviceConfig
from sonofflan.devices.thermoplug import ThermoPlug
from tests import get_and_wait


def test_create():
    before = get_and_wait()
    dev = ThermoPlug(
        {
            "id": "1234",
            "type": "th_plug",
            "address": "address",
            "port": 123,
            "encrypt": False,
            "data": {
                "switch": "on",
                "sensorType": "Sensor Type",
                "currentTemperature": 20.00,
                "currentHumidity": 55,
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
    assert dev.sensor == "Sensor Type"
    assert dev.temperature == 20.00
    assert dev.humidity == 55


def test_update():
    before = get_and_wait()
    dev = ThermoPlug(
        {
            "id": "1234",
            "type": "th_plug",
            "address": "address",
            "port": 123,
            "encrypt": False,
            "data": {
                "switch": "on",
                "sensorType": "Sensor Type",
                "currentTemperature": 20.00,
                "currentHumidity": 55,
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
    assert dev.sensor == "Sensor Type"
    assert dev.temperature == 20.00
    assert dev.humidity == 55

    dev.update({
        "id": "1234",
        "type": "th_plug",
        "address": "address",
        "port": 123,
        "encrypt": False,
        "data": {
            "switch": "off",
            "sensorType": "Sensor Type",
            "currentTemperature": 21.57,
            "currentHumidity": 63,
        },
    })
    after_update = get_and_wait()

    assert after < after_update
    assert dev.last_update > after  # type: ignore
    assert dev.last_update < after_update  # type: ignore
    assert dev.status is False
    assert dev.sensor == "Sensor Type"
    assert dev.temperature == 21.57
    assert dev.humidity == 63
