import asyncio
import json
import logging
from unittest.mock import AsyncMock

import pytest

from zeroconf import ServiceInfo, ServiceStateChange

from sonofflan.browser import Browser
from sonofflan.config import DevicesConfig
from sonofflan.crypto import encrypt, generate_iv
from sonofflan.devices import Plug, PowerPlug

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

    # noinspection PyMethodMayBeStatic
    async def async_get_service_info(self, service_type: str, name: str) -> ServiceInfo:
        assert name.endswith("." + service_type)
        device_id = name[:-(len(service_type) + 1)]
        if device_id.startswith("eWeLink_"):
            device_id = device_id[8:]
        if device_id == "1234":
            data = {
                "switch": "on",
            }
            prop = {
                b"id": b"1234",
                b"type": b"plug",
                b"data1": json.dumps(data).encode("utf8"),
            }
        elif device_id == "5678":
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
    # noinspection PyTypeChecker
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
    dev = browser.devices["1234"]
    assert dev.name == "Device 1"
    assert dev.url == "http://1.2.3.4:8181"
    assert dev.encrypt is False
    assert isinstance(dev, Plug)
    assert dev.status is True


@pytest.mark.asyncio
async def test_add_two(class_mocker):
    class_mocker.patch('sonofflan.browser.AsyncZeroconf', new=AsyncZeroconfMock)
    class_mocker.patch('sonofflan.browser.AsyncServiceBrowser', new=AsyncServiceBrowserMock)

    browser = Browser(config)
    # noinspection PyTypeChecker
    browser._update(
        zeroconf=None,
        service_type="_ewelink._tcp.local.",
        name="eWeLink_1234._ewelink._tcp.local.",
        state_change=ServiceStateChange.Added
    )
    # noinspection PyTypeChecker
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
    dev = browser.devices["1234"]
    assert dev.name == "Device 1"
    assert dev.url == "http://1.2.3.4:8181"
    assert dev.encrypt is False
    assert isinstance(dev, Plug)
    assert dev.status is True

    assert "5678" in browser.devices
    dev = browser.devices["5678"]
    assert dev.name == "Device 2"
    assert dev.url == "http://1.2.3.4:8181"
    assert dev.encrypt is True
    assert isinstance(dev, PowerPlug)
    assert dev.status is True
    assert dev.voltage == 220.00
    assert dev.current == 5.00
    assert dev.power == 1100.00


@pytest.mark.asyncio
async def test_queue(class_mocker):
    class_mocker.patch('sonofflan.browser.AsyncZeroconf', new=AsyncZeroconfMock)
    class_mocker.patch('sonofflan.browser.AsyncServiceBrowser', new=AsyncServiceBrowserMock)

    browser = Browser(config)

    events = []

    # Create a task that collect events
    async def processor(ev_list: list):
        while True:
            ev = await browser.wait_event()
            logger.info(f"Got event {ev.action} for {ev.device}")
            ev_list += [ev]
            browser.event_processed()
    task = asyncio.create_task(processor(events))

    # noinspection PyTypeChecker
    browser._update(
        zeroconf=None,
        service_type="_ewelink._tcp.local.",
        name="eWeLink_1234._ewelink._tcp.local.",
        state_change=ServiceStateChange.Added
    )
    # noinspection PyTypeChecker
    browser._update(
        zeroconf=None,
        service_type="_ewelink._tcp.local.",
        name="eWeLink_5678._ewelink._tcp.local.",
        state_change=ServiceStateChange.Added
    )
    # noinspection PyTypeChecker
    browser._update(
        zeroconf=None,
        service_type="_ewelink._tcp.local.",
        name="eWeLink_1234._ewelink._tcp.local.",
        state_change=ServiceStateChange.Updated
    )

    # Wait for all events processed
    await asyncio.sleep(1)
    await browser._queue.join()
    task.cancel()
    await browser.shutdown()

    logger.info("Events:")
    for ev in events:
        logger.info(f"  {ev.action.name} for {ev.device}")
    assert len(events) == 3
    event = events.pop(0)
    assert event.action == ServiceStateChange.Added
    assert event.device.id == "1234"
    assert event.device is not browser.devices["1234"]  # Check that it was copied
    event = events.pop(0)
    assert event.action == ServiceStateChange.Added
    assert event.device.id == "5678"
    assert event.device is not browser.devices["5678"]  # Check that it was copied
    event = events.pop(0)
    assert event.action == ServiceStateChange.Updated
    assert event.device.id == "1234"
    assert event.device is not browser.devices["1234"]  # Check that it was copied
