class DeviceConfig:
    """Hold device configuration.

    Configuration is loaded by dictionary.
    ID is the only required field. Name is used for display and ID will
    be used if not set.
    Key is required only for encrypted devices (not DIY mode).

    Attributes
    ----------
    `id` : str
        ID of the device
    `name` : str
        Name of the device (if not set, the ID will be used)
    `key` : str|None
        Encryption key for the device (used only if the device is encrypted).
    """

    def __init__(self, c: dict) -> None:
        """
        Parameters
        ----------
        `c` : dict
            Dictionary with the configuration
        """

        if not isinstance(c, dict):
            raise TypeError(f"Invalid parameter \"{c}\" ({type(c).__name__}): expected a dictionary")
        if "id" not in c:
            raise ValueError(f"Missing required ID in {c}")
        self._id = str(c["id"])
        self._name = None
        self._key = None
        if "name" in c:
            self._name = c["name"]
        if "key" in c and c["key"] != "":
            self._key = c["key"]

    def __repr__(self) -> str:
        return f"DeviceConfig(\"{self._name}\" id:{self._id} key:{self._key})"

    @property
    def id(self) -> str:
        """The device ID"""

        return self._id

    @property
    def name(self) -> str:
        """The device name (or the ID if not set)"""

        return self._name if self._name is not None else f"[{self._id}]"

    @property
    def key(self) -> str | None:
        """The device encryption key (or None if not set)"""

        return self._key


class DevicesConfig:
    """Hold the configuration for all the devices.

    Configuration is loaded by list of dictionaries or by dictionary:

        [
            {
                "id": "1234",
                "name": "Device 1"
            },
            {
                "id": "5678",
                "name": "Device 2"
            }
        ]

    or

        {
            "1234": {
                "name": "Device 1"
            },
            "5678" : {
                "name": "Device 2"
            }
        }
    """

    def __init__(self, c: dict | list | None = None) -> None:
        """
        Parameters
        ----------
        `c` : dict|list
            Dictionary or list with the configuration (optional)
        """

        self._devices = {}
        if c is None:
            return  # Nothing to configure
        if isinstance(c, dict):
            # Configure from dictionary: ID is in the key
            for device_id in c:
                c[device_id]["id"] = device_id  # In that case field "id" is replaced with the key
                self._devices[device_id] = DeviceConfig(c[device_id])
        elif isinstance(c, list):
            # Configure from list: ID is in the item
            for it in c:
                dc = DeviceConfig(it)
                self._devices[dc.id] = dc
        else:
            raise TypeError(f"Invalid parameter \"{c}\" ({type(c).__name__}): expected a dictionary or a list")

    def __repr__(self) -> str:
        return f"DevicesConfig({self._devices})"

    def num_devices(self) -> int:
        """Get the number of configured devices"""

        return len(self._devices)

    def device(self, device_id: str) -> DeviceConfig | None:
        """Get the configuration for the device with the specified ID

        Parameters
        ----------
        `device_id` : str
            The ID for the device to retrieve
        """

        if device_id in self._devices:
            return self._devices[device_id]
        return None
