class DeviceConfig:
    """Hold device configuration.

    Configurations is loaded by dictionary.
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

    _id = None
    _name = None
    _key = None

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
        self._id = c["id"]
        if "name" in c:
            self._name = c["name"]
        if "key" in c and c["key"] != "":
            self._key = c["key"]

    @property
    def id(self) -> str:
        """The device ID"""

        return self._id

    @property
    def name(self) -> str:
        """The device name (or the ID if not set)"""

        return self._name if self._name is not None else f"[{self._id}]"

    @property
    def key(self) -> str|None:
        """The device encryption key (or None if not set)"""

        return self._key
