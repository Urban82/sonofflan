import asyncio
import json
import logging
from typing import Callable

from zeroconf import ServiceStateChange, Zeroconf
from zeroconf.asyncio import AsyncServiceBrowser, AsyncZeroconf

from sonofflan.config import DeviceConfig, DevicesConfig
from sonofflan.crypto import decrypt
from sonofflan.devices import create_device, Device
from sonofflan.errors import (
    InvalidDeviceError,
    MissingDeviceKeyError,
    NoInfoError,
    NotConfiguredDeviceError
)
from sonofflan.utils import parse_address

SERVICE_TYPE = "_ewelink._tcp.local."
DEVICE_PREFIX = "eWeLink_"


class Browser():
    """Zeroconf browser for Sonoff devices

    Attributes
    ----------
    `devices` : dict
        Dictionary with the devices that were found
    """

    def __init__(self, config: DevicesConfig):
        """
        Parameters
        ----------
        `config` : DevicesConfig
            Configuration for the device
        """

        self._config = config
        self._devices = {}
        self._logger = logging.getLogger(f"sonofflan.browser")

        self._logger.debug("Starting...")
        self._zeroconf = AsyncZeroconf()
        self._browser = AsyncServiceBrowser(self._zeroconf.zeroconf, SERVICE_TYPE, handlers=[self._update])

    async def shutdown(self) -> None:
        """Shutdown the browser"""

        self._logger.debug("Stopping...")
        await self._browser.async_cancel()
        self._logger.debug("Stopped")

    @property
    def devices(self) -> dict[str, Device]:
        """The devices that were found"""

        return self._devices

    def _update(self, zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange) -> None:
        asyncio.get_running_loop().create_task(
            self._async_update(service_type, name, state_change)
        )

    async def _async_update(self, service_type: str, name: str, state_change: ServiceStateChange):
        try:
            self._logger.debug(f'Service:"{name}" Action:{state_change.name}')
            if not name.startswith(DEVICE_PREFIX) or not name.endswith("." + SERVICE_TYPE):
                raise InvalidDeviceError(name)
            info = await self._zeroconf.async_get_service_info(service_type, name)
            if info is None:
                raise NoInfoError(name)
            device_id = info.properties.get(b"id").decode("utf8")
            device_type = info.properties.get(b"type").decode("utf8")
            config = self._config.device(device_id)
            if config is None:
                raise NotConfiguredDeviceError(device_id, device_type)
            self._logger.debug(f"Got config {config}")
            extra = b"".join(map(lambda x : info.properties.get(x) or b"", [b"data1", b"data2", b"data3", b"data4"]))
            encrypt = (info.properties.get(b"encrypt") == b"true")
            if encrypt:
                if config.key == None:
                    raise MissingDeviceKeyError(device_id, device_type)
                iv = info.properties.get(b"iv").decode("utf8")
                extra = decrypt(extra.decode("utf8"), iv, config.key)
            data = {
                "id": device_id,
                "type": device_type,
                "address": parse_address(info.addresses[0]),
                "port": info.port,
                "encrypt": encrypt,
                "data": json.loads(extra.decode("utf8"))
            }
            self._logger.info(f"{state_change.name} device id:{data['id']} type:{data['type']} name:{config.name}")
            if data['id'] not in self._devices:
                self._devices[data['id']] = create_device(data, config)
            device = self._devices[data['id']]
            if state_change != ServiceStateChange.Removed:
                device.update(data)
            else:
                # TODO Maybe set as offline?
                pass
            self._logger.info(f"{state_change.name} {device}")
        except InvalidDeviceError as ex:
            self._logger.warn(f'{ex}, ignoring it')
        except NoInfoError as ex:
            self._logger.warn(f'{ex}, ignoring it')
        except NotConfiguredDeviceError as ex:
            self._logger.debug(f'{ex}, ignoring it')
        except Exception:
            self._logger.error(f'Exception while processing {state_change.name} for "{name}" [{service_type}], ignoring it', exc_info=True)
