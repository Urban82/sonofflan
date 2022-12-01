import asyncio
import json

import pytest
import requests_mock

from sonofflan.config import DeviceConfig
from sonofflan.devices.plug import Plug
from tests import get_and_wait


def test_create():
    before = get_and_wait()
    dev = Plug(
        {
            "id": "1234",
            "type": "plug",
            "address": "address",
            "port": 123,
            "encrypt": False,
            "data": {
                "switch": "on",
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


def test_update():
    before = get_and_wait()
    dev = Plug(
        {
            "id": "1234",
            "type": "plug",
            "address": "address",
            "port": 123,
            "encrypt": False,
            "data": {
                "switch": "on",
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

    dev.update({
        "id": "1234",
        "type": "plug",
        "address": "address",
        "port": 123,
        "encrypt": False,
        "data": {
            "switch": "off",
        },
    })
    after_update = get_and_wait()

    assert after < after_update
    assert dev.last_update > after  # type: ignore
    assert dev.last_update < after_update  # type: ignore
    assert dev.status is False


@pytest.mark.asyncio
async def test_on():
    dev = Plug(
        {
            "id": "1234",
            "type": "plug",
            "address": "address",
            "port": 123,
            "encrypt": False,
            "data": {
                "switch": "on",
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
        m.post(requests_mock.ANY, json={"error": 0})
        dev.on()

        await asyncio.sleep(1)

    assert m.called
    assert m.call_count == 1
    assert m.last_request.method == "POST"
    assert m.last_request.scheme == "http"
    assert m.last_request.hostname == "address"
    assert m.last_request.port == 123
    assert m.last_request.path == "/zeroconf/switch"
    data = json.loads(m.last_request.text)
    assert "sequence" in data
    assert data["deviceid"] == "1234"
    assert data["encrypt"] is False
    assert json.loads(data["data"]) == {"switch": "on"}


@pytest.mark.asyncio
async def test_off():
    dev = Plug(
        {
            "id": "1234",
            "type": "plug",
            "address": "address",
            "port": 123,
            "encrypt": False,
            "data": {
                "switch": "off",
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
        m.post(requests_mock.ANY, json={"error": 0})
        dev.off()

        await asyncio.sleep(1)

    assert m.called
    assert m.call_count == 1
    assert m.last_request.method == "POST"
    assert m.last_request.scheme == "http"
    assert m.last_request.hostname == "address"
    assert m.last_request.port == 123
    assert m.last_request.path == "/zeroconf/switch"
    data = json.loads(m.last_request.text)
    assert "sequence" in data
    assert data["deviceid"] == "1234"
    assert data["encrypt"] is False
    assert json.loads(data["data"]) == {"switch": "off"}


@pytest.mark.asyncio
async def test_toggle():
    dev = Plug(
        {
            "id": "1234",
            "type": "plug",
            "address": "address",
            "port": 123,
            "encrypt": False,
            "data": {
                "switch": "on",
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
        m.post(requests_mock.ANY, json={"error": 0})
        dev.toggle()

        await asyncio.sleep(1)

    assert m.called
    assert m.call_count == 1
    assert m.last_request.method == "POST"
    assert m.last_request.scheme == "http"
    assert m.last_request.hostname == "address"
    assert m.last_request.port == 123
    assert m.last_request.path == "/zeroconf/switch"
    data = json.loads(m.last_request.text)
    assert "sequence" in data
    assert data["deviceid"] == "1234"
    assert data["encrypt"] is False
    assert json.loads(data["data"]) == {"switch": "off"}

    m.reset()

    dev.update({
        "id": "1234",
        "type": "plug",
        "address": "address",
        "port": 123,
        "encrypt": False,
        "data": {
            "switch": "off",
        },
    })

    with requests_mock.Mocker() as m:
        m.post(requests_mock.ANY, json={"error": 0})
        dev.toggle()

        await asyncio.sleep(1)

    assert m.called
    assert m.call_count == 1
    assert m.last_request.method == "POST"
    assert m.last_request.scheme == "http"
    assert m.last_request.hostname == "address"
    assert m.last_request.port == 123
    assert m.last_request.path == "/zeroconf/switch"
    data = json.loads(m.last_request.text)
    assert "sequence" in data
    assert data["deviceid"] == "1234"
    assert data["encrypt"] is False
    assert json.loads(data["data"]) == {"switch": "on"}


@pytest.mark.asyncio
async def test_refresh():
    dev = Plug(
        {
            "id": "1234",
            "type": "plug",
            "address": "address",
            "port": 123,
            "encrypt": False,
            "data": {
                "switch": "on",
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
        m.post(requests_mock.ANY, json={"error": 0})
        dev.refresh()

        await asyncio.sleep(1)

    assert m.called
    assert m.call_count == 1
    assert m.last_request.method == "POST"
    assert m.last_request.scheme == "http"
    assert m.last_request.hostname == "address"
    assert m.last_request.port == 123
    assert m.last_request.path == "/zeroconf/switch"
    data = json.loads(m.last_request.text)
    assert "sequence" in data
    assert data["deviceid"] == "1234"
    assert data["encrypt"] is False
    assert json.loads(data["data"]) == {"switch": "on"}

    m.reset()

    dev.update({
        "id": "1234",
        "type": "plug",
        "address": "address",
        "port": 123,
        "encrypt": False,
        "data": {
            "switch": "off",
        },
    })

    with requests_mock.Mocker() as m:
        m.post(requests_mock.ANY, json={"error": 0})
        dev.refresh()

        await asyncio.sleep(1)

    assert m.called
    assert m.call_count == 1
    assert m.last_request.method == "POST"
    assert m.last_request.scheme == "http"
    assert m.last_request.hostname == "address"
    assert m.last_request.port == 123
    assert m.last_request.path == "/zeroconf/switch"
    data = json.loads(m.last_request.text)
    assert "sequence" in data
    assert data["deviceid"] == "1234"
    assert data["encrypt"] is False
    assert json.loads(data["data"]) == {"switch": "off"}
