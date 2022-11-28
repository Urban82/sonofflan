import asyncio
import json
import logging
import time
from collections import OrderedDict
from datetime import datetime

import requests

from sonofflan.config import DeviceConfig
from sonofflan.crypto import encrypt, generate_iv


class Device:
    """Base sonoff device

    Attributes
    ----------
    `id` : str
        The device ID
    `name` : str
        The device name (from configuration)
    `encrypt` : bool
        If the device is encrypted (not DIY mode)
    `key` : str
        The device encryption key (from configuration)
    `url` : str
        The device base URL (used to send commands)
    `last_update` : datetime
        The date and time which the device was updated for the last time
    """

    def __init__(self, data: dict, config: DeviceConfig) -> None:
        """
        Parameters
        ----------
        `data` : dict
            Dictionary with data coming from Zeroconf
        `config` : DeviceConfig
            Configuration for the device
        """

        self._id = config.id
        self._name = config.name
        self._encrypt = data['encrypt']
        self._key = config.key
        self._url = None
        self._last_update = None
        self._logger = logging.getLogger(f"sonofflan.devices.{self.__class__.__name__}")

        self._update(data)

    def _update(self, data: dict) -> None:
        """Internal update method

        Parameters
        ----------
        `data` : dict
            Dictionary with data coming from Zeroconf
        """

        self._encrypt = data['encrypt']
        self._url = f"http://{data['address']}:{data['port']}"
        self._last_update = datetime.now()

    def update(self, data: dict) -> None:
        """Update the device with data from Zeroconf

        Parameters
        ----------
        `data` : dict
            Dictionary with data coming from Zeroconf
        """

        self._logger.debug(f'Updating {self} with {json.dumps(data, indent=2)}')
        if self._id != data['id']:
            self._logger.error(f"Unexpected update for {self} with {data}")
            return
        self._update(data)

    def _repr(self) -> str:
        """Internal representation method"""

        return f'"{self._name}" {self._id} url={self._url} encrypt={self._encrypt}'

    def __repr__(self) -> str:
        """Representation method"""

        return f'{self.__class__.__name__}({self._repr()} updated={self._last_update})'

    def _send(self, url: str, data: str|dict) -> None:
        """Internal send command method

        Parameters
        ----------
        `url` : str
            Command URL
        `data` : str|dict
            Data for the command
        """

        asyncio.get_running_loop().create_task(
            self._async_send(url, data)
        )

    async def _async_send(self, url: str, data: str|dict) -> None:
        """Internal asynchronous send command method

        Parameters
        ----------
        `url` : str
            Command URL
        `data` : str|dict
            Data for the command
        """

        if self._url is None:
            self._logger.error(f"Cannot send commands to {self}: url not valid")
            return

        if type(data) == dict:
            data = json.dumps(data, separators=(",", ":"), indent=None)
        self._logger.debug(f'Sending to "{self._url}{url}" data "{data}"')
        payload = {
            "sequence": str(int(time.time() * 1000)),
            "deviceid": self._id,
            "encrypt": self._encrypt,
        }
        if self._encrypt and self._key is not None:
            payload["selfApikey"] = "123"
            iv = generate_iv()
            payload["iv"] = iv
            data = encrypt(data, iv, self._key)  # type: ignore
        payload["data"] = data

        headers = OrderedDict(
            {
                "Content-Type": "application/json;charset=UTF-8",
                # "Connection": "keep-alive",
                "Accept": "application/json",
                "Accept-Language": "en-gb",
                # "Content-Length": "0",
                # "Accept-Encoding": "gzip, deflate",
                # "Cache-Control": "no-store",
            }
        )
        payload = json.dumps(payload, separators=(",", ":"), indent=None)
        response = requests.post(f"{self._url}{url}", headers=headers, data=payload)
        try:
            if response.status_code != 200:
                raise RuntimeError(f"Got HTTP status {response.code}")  # type: ignore
            response_json = json.loads(response.content.decode("utf-8"))
            self._logger.debug(f'Got response {response.status_code} {json.dumps(response_json, indent=2)}')
            if "error" in response_json and response_json["error"] != 0:
                raise RuntimeError(f'Get error {response_json["error"]}')
            self._logger.debug(f'Message sent to {self} successfully!')
        except Exception as ex:
            self._logger.error(f"Error processing response {response}: {response.content}", exc_info=True)

    @property
    def id(self) -> str:
        """The device ID"""

        return self._id  # type: ignore

    @property
    def name(self) -> str:
        """The device name"""

        return self._name  # type: ignore

    @property
    def encrypt(self) -> bool:
        """If the device is encrypted (not DIY mode)"""

        return self._encrypt

    @property
    def key(self) -> str|None:
        """The device encryption key"""

        return self._key

    @property
    def url(self) -> str|None:
        """The device base URL (used to send commands)"""

        return self._url

    @property
    def last_update(self) -> datetime|None:
        """The date and time which the device was updated for the last time"""

        return self._last_update
