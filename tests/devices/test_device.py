import asyncio
import json

import pytest
import requests_mock

from sonofflan.config import DeviceConfig
from sonofflan.crypto import decrypt, encrypt, generate_iv
from sonofflan.devices.device import Device
from tests import get_and_wait


def test_create():
    before = get_and_wait()
    dev = Device(
        {
            "id": "1234",
            "type": "device_type",
            "address": "address",
            "port": 123,
            "encrypt": False,
            "data": {},
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
    assert dev.encrypt == False
    assert dev.key is None
    assert dev.url == "http://address:123"
    assert before < after
    assert dev.last_update > before  # type: ignore
    assert dev.last_update < after  # type: ignore

def test_update():
    before = get_and_wait()
    dev = Device(
        {
            "id": "1234",
            "type": "device_type",
            "address": "address",
            "port": 123,
            "encrypt": False,
            "data": {},
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

    dev.update({
        "id": "1234",
        "type": "device_type",
        "address": "address",
        "port": 123,
        "encrypt": False,
        "data": {},
    })
    after_update = get_and_wait()

    assert after < after_update
    assert dev.last_update > after  # type: ignore
    assert dev.last_update < after_update  # type: ignore

@pytest.mark.asyncio
async def test_send():
    dev = Device(
        {
            "id": "1234",
            "type": "device_type",
            "address": "address",
            "port": 123,
            "encrypt": False,
            "data": {},
        },
        DeviceConfig(
            {
                "id": "1234",
                "name": "Device 1",
            }
        )
    )

    with requests_mock.Mocker() as m:
        m.post(requests_mock.ANY, json={"error":0})
        dev._send("/command/path", {"parameter": "value"})

        await asyncio.sleep(1)

    assert m.called
    assert m.call_count == 1
    assert m.last_request.method == "POST"
    assert m.last_request.scheme == "http"
    assert m.last_request.hostname == "address"
    assert m.last_request.port == 123
    assert m.last_request.path == "/command/path"
    data = json.loads(m.last_request.text)
    assert "sequence" in data
    assert data["deviceid"] == "1234"
    assert data["encrypt"] == False
    assert json.loads(data["data"]) == {"parameter": "value"}

@pytest.mark.asyncio
async def test_send_crypto():
    iv = generate_iv()
    dev_key = "testing key"
    dev = Device(
        {
            "id": "1234",
            "type": "device_type",
            "address": "address",
            "port": 123,
            "encrypt": True,
            "iv": iv,
            "data": encrypt("{}", iv, dev_key),
        },
        DeviceConfig(
            {
                "id": "1234",
                "name": "Device 1",
                "key": dev_key,
            }
        )
    )

    with requests_mock.Mocker() as m:
        m.post(requests_mock.ANY, json={"error":0})
        dev._send("/command/path", {"parameter": "value"})

        await asyncio.sleep(1)

    assert m.called
    assert m.call_count == 1
    assert m.last_request.method == "POST"
    assert m.last_request.scheme == "http"
    assert m.last_request.hostname == "address"
    assert m.last_request.port == 123
    assert m.last_request.path == "/command/path"
    data = json.loads(m.last_request.text)
    assert "sequence" in data
    assert data["deviceid"] == "1234"
    assert data["encrypt"] == True
    assert data["selfApikey"] == "123"
    assert "iv" in data
    iv = data["iv"]
    assert json.loads(decrypt(data["data"], iv, dev_key)) == {"parameter": "value"}
