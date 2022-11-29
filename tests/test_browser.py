import asyncio
import json
import logging
from unittest.mock import AsyncMock

import pytest

from zeroconf import ServiceInfo, ServiceStateChange

from sonofflan.browser import Browser
from sonofflan.config import DevicesConfig
from sonofflan.crypto import encrypt, generate_iv

dev2key = "abcdefgh-ijkl-mnop-qrst-uvwxyz012345"
config = DevicesConfig([
    {
        "id": "1234",
        "name": "Device 1"
    },
    {
        "id": "5678",
        "name": "Device 2",
        "key": dev2key
    }
])

logger = logging.getLogger("test_browser")


class AsyncZeroconfMock(AsyncMock):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def async_get_service_info(self, service_type: str, name: str) -> ServiceInfo:
        assert name.endswith("." + service_type)
        id = name[:-(len(service_type) + 1)]
        if id.startswith("eWeLink_"):
            id = id[8:]
        if id == "1234":
            data = {
                "switch": "on",
            }
            prop = {
                b"id": b"1234",
                b"type": b"plug",
                b"data1": json.dumps(data).encode("utf8"),
            }
        elif id == "5678":
            iv = generate_iv()
            data = {
                "switch": "on",
                "voltage": 220.00,
                "current": 5.00,
                "power": 1100.00,
            }
            prop = {
                b"id": b"5678",
                b"type": b"enhanced_plug",
                b"encrypt": b"true",
                b"iv": iv.encode("utf8"),
                b"data1": encrypt(json.dumps(data), iv, dev2key).encode("utf8"),
            }
        else:
            prop = b""
        return ServiceInfo(
            type_=service_type,
            name=name,
            addresses=[bytes([1, 2, 3, 4])],
            port=8181,
            properties=prop
        )


class AsyncServiceBrowserMock(AsyncMock):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.async_cancel_called = 0

    async def async_cancel(self):
        self.async_cancel_called += 1


@pytest.mark.asyncio
async def test_shutdown(class_mocker):
    class_mocker.patch('sonofflan.browser.AsyncZeroconf', new=AsyncZeroconfMock)
    class_mocker.patch('sonofflan.browser.AsyncServiceBrowser', new=AsyncServiceBrowserMock)

    browser = Browser(config)
    await browser.shutdown()

    assert browser._browser.async_cancel_called == 1
    assert len(browser.devices) == 0

@pytest.mark.asyncio
async def test_add(class_mocker):
    class_mocker.patch('sonofflan.browser.AsyncZeroconf', new=AsyncZeroconfMock)
    class_mocker.patch('sonofflan.browser.AsyncServiceBrowser', new=AsyncServiceBrowserMock)

    browser = Browser(config)
    browser._update(
        zeroconf=None,
        service_type="_ewelink._tcp.local.",
        name="eWeLink_1234._ewelink._tcp.local.",
        state_change=ServiceStateChange.Added
    )
    await asyncio.sleep(1)
    await browser.shutdown()

    assert browser._browser.async_cancel_called == 1
    assert len(browser.devices) == 1

    assert "1234" in browser.devices
    assert browser.devices["1234"].name == "Device 1"
    assert browser.devices["1234"].url == "http://1.2.3.4:8181"
    assert browser.devices["1234"].encrypt == False
    assert browser.devices["1234"].status == True

@pytest.mark.asyncio
async def test_add_two(class_mocker):
    class_mocker.patch('sonofflan.browser.AsyncZeroconf', new=AsyncZeroconfMock)
    class_mocker.patch('sonofflan.browser.AsyncServiceBrowser', new=AsyncServiceBrowserMock)

    browser = Browser(config)
    browser._update(
        zeroconf=None,
        service_type="_ewelink._tcp.local.",
        name="eWeLink_1234._ewelink._tcp.local.",
        state_change=ServiceStateChange.Added
    )
    browser._update(
        zeroconf=None,
        service_type="_ewelink._tcp.local.",
        name="eWeLink_5678._ewelink._tcp.local.",
        state_change=ServiceStateChange.Added
    )
    await asyncio.sleep(1)
    await browser.shutdown()

    assert browser._browser.async_cancel_called == 1
    assert len(browser.devices) == 2

    assert "1234" in browser.devices
    assert browser.devices["1234"].name == "Device 1"
    assert browser.devices["1234"].url == "http://1.2.3.4:8181"
    assert browser.devices["1234"].encrypt == False
    assert browser.devices["1234"].status == True

    assert "5678" in browser.devices
    assert browser.devices["5678"].name == "Device 2"
    assert browser.devices["5678"].url == "http://1.2.3.4:8181"
    assert browser.devices["5678"].encrypt == True
    assert browser.devices["5678"].status == True
    assert browser.devices["5678"].voltage == 220.00
    assert browser.devices["5678"].current == 5.00
    assert browser.devices["5678"].power == 1100.00
