import asyncio
import json

import pytest
import requests_mock

from sonofflan.config import DeviceConfig
from sonofflan.devices.strip import Strip
from tests import get_and_wait


def test_create():
    before = get_and_wait()
    dev = Strip(
        {
            "id": "1234",
            "type": "strip",
            "address": "address",
            "port": 123,
            "encrypt": False,
            "data": {
                "switches": [
                    {
                        "outlet": 0,
                        "switch": "on",
                    },
                    {
                        "outlet": 1,
                        "switch": "off",
                    },
                ],
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
    assert dev.encrypt == False
    assert dev.key is None
    assert dev.url == "http://address:123"
    assert before < after
    assert dev.last_update > before  # type: ignore
    assert dev.last_update < after  # type: ignore
    assert dev.outlets == [0, 1]
    assert dev.status(0) == True
    assert dev.status(1) == False
    with pytest.raises(ValueError):
        dev.status(2)

def test_update():
    before = get_and_wait()
    dev = Strip(
        {
            "id": "1234",
            "type": "stripe",
            "address": "address",
            "port": 123,
            "encrypt": False,
            "data": {
                "switches": [
                    {
                        "outlet": 0,
                        "switch": "on",
                    },
                    {
                        "outlet": 1,
                        "switch": "off",
                    },
                ],
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
    assert dev.outlets == [0, 1]
    assert dev.status(0) == True
    assert dev.status(1) == False

    dev.update({
        "id": "1234",
        "type": "stripe",
        "address": "address",
        "port": 123,
        "encrypt": False,
        "data": {
            "switches": [
                {
                    "outlet": 0,
                    "switch": "off",
                },
                {
                    "outlet": 1,
                    "switch": "on",
                },
            ],
        },
    })
    after_update = get_and_wait()

    assert after < after_update
    assert dev.last_update > after  # type: ignore
    assert dev.last_update < after_update  # type: ignore
    assert dev.outlets == [0, 1]
    assert dev.status(0) == False
    assert dev.status(1) == True

@pytest.mark.asyncio
async def test_on():
    dev = Strip(
        {
            "id": "1234",
            "type": "stripe",
            "address": "address",
            "port": 123,
            "encrypt": False,
            "data": {
                "switches": [
                    {
                        "outlet": 0,
                        "switch": "on",
                    },
                    {
                        "outlet": 1,
                        "switch": "off",
                    },
                ],
            },
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
        dev.on(1)

        await asyncio.sleep(1)

    assert m.called
    assert m.call_count == 1
    assert m.last_request.method == "POST"
    assert m.last_request.scheme == "http"
    assert m.last_request.hostname == "address"
    assert m.last_request.port == 123
    assert m.last_request.path == "/zeroconf/switches"
    data = json.loads(m.last_request.text)
    assert "sequence" in data
    assert data["deviceid"] == "1234"
    assert data["encrypt"] == False
    assert json.loads(data["data"]) == {'switches': [{'outlet': 1, 'switch': 'on'}]}

@pytest.mark.asyncio
async def test_off():
    dev = Strip(
        {
            "id": "1234",
            "type": "stripe",
            "address": "address",
            "port": 123,
            "encrypt": False,
            "data": {
                "switches": [
                    {
                        "outlet": 0,
                        "switch": "on",
                    },
                    {
                        "outlet": 1,
                        "switch": "off",
                    },
                ],
            },
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
        dev.off(1)

        await asyncio.sleep(1)

    assert m.called
    assert m.call_count == 1
    assert m.last_request.method == "POST"
    assert m.last_request.scheme == "http"
    assert m.last_request.hostname == "address"
    assert m.last_request.port == 123
    assert m.last_request.path == "/zeroconf/switches"
    data = json.loads(m.last_request.text)
    assert "sequence" in data
    assert data["deviceid"] == "1234"
    assert data["encrypt"] == False
    assert json.loads(data["data"]) == {'switches': [{'outlet': 1, 'switch': 'off'}]}

@pytest.mark.asyncio
async def test_toggle():
    dev = Strip(
        {
            "id": "1234",
            "type": "stripe",
            "address": "address",
            "port": 123,
            "encrypt": False,
            "data": {
                "switches": [
                    {
                        "outlet": 0,
                        "switch": "on",
                    },
                    {
                        "outlet": 1,
                        "switch": "off",
                    },
                ],
            },
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
        dev.toggle(1)

        await asyncio.sleep(1)

    assert m.called
    assert m.call_count == 1
    assert m.last_request.method == "POST"
    assert m.last_request.scheme == "http"
    assert m.last_request.hostname == "address"
    assert m.last_request.port == 123
    assert m.last_request.path == "/zeroconf/switches"
    data = json.loads(m.last_request.text)
    assert "sequence" in data
    assert data["deviceid"] == "1234"
    assert data["encrypt"] == False
    assert json.loads(data["data"]) == {'switches': [{'outlet': 1, 'switch': 'on'}]}

    m.reset()

    dev.update({
        "id": "1234",
        "type": "stripe",
        "address": "address",
        "port": 123,
        "encrypt": False,
        "data": {
            "switches": [
                {
                    "outlet": 0,
                    "switch": "on",
                },
                {
                    "outlet": 1,
                    "switch": "on",
                },
            ],
        },
    })

    with requests_mock.Mocker() as m:
        m.post(requests_mock.ANY, json={"error":0})
        dev.toggle(1)

        await asyncio.sleep(1)

    assert m.called
    assert m.call_count == 1
    assert m.last_request.method == "POST"
    assert m.last_request.scheme == "http"
    assert m.last_request.hostname == "address"
    assert m.last_request.port == 123
    assert m.last_request.path == "/zeroconf/switches"
    data = json.loads(m.last_request.text)
    assert "sequence" in data
    assert data["deviceid"] == "1234"
    assert data["encrypt"] == False
    assert json.loads(data["data"]) == {'switches': [{'outlet': 1, 'switch': 'off'}]}

@pytest.mark.asyncio
async def test_refresh():
    dev = Strip(
        {
            "id": "1234",
            "type": "stripe",
            "address": "address",
            "port": 123,
            "encrypt": False,
            "data": {
                "switches": [
                    {
                        "outlet": 0,
                        "switch": "on",
                    },
                    {
                        "outlet": 1,
                        "switch": "off",
                    },
                ],
            },
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
        dev.refresh(1)

        await asyncio.sleep(1)

    assert m.called
    assert m.call_count == 1
    assert m.last_request.method == "POST"
    assert m.last_request.scheme == "http"
    assert m.last_request.hostname == "address"
    assert m.last_request.port == 123
    assert m.last_request.path == "/zeroconf/switches"
    data = json.loads(m.last_request.text)
    assert "sequence" in data
    assert data["deviceid"] == "1234"
    assert data["encrypt"] == False
    assert json.loads(data["data"]) == {'switches': [{'outlet': 1, 'switch': 'off'}]}

    m.reset()

    dev.update({
        "id": "1234",
        "type": "stripe",
        "address": "address",
        "port": 123,
        "encrypt": False,
        "data": {
            "switches": [
                {
                    "outlet": 0,
                    "switch": "on",
                },
                {
                    "outlet": 1,
                    "switch": "on",
                },
            ],
        },
    })

    with requests_mock.Mocker() as m:
        m.post(requests_mock.ANY, json={"error":0})
        dev.refresh(1)

        await asyncio.sleep(1)

    assert m.called
    assert m.call_count == 1
    assert m.last_request.method == "POST"
    assert m.last_request.scheme == "http"
    assert m.last_request.hostname == "address"
    assert m.last_request.port == 123
    assert m.last_request.path == "/zeroconf/switches"
    data = json.loads(m.last_request.text)
    assert "sequence" in data
    assert data["deviceid"] == "1234"
    assert data["encrypt"] == False
    assert json.loads(data["data"]) == {'switches': [{'outlet': 1, 'switch': 'on'}]}
