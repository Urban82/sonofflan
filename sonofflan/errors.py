class InvalidDeviceError(RuntimeError):
    """The device has an invalid type"""

    def __init__(self, name: str) -> None:
        super().__init__(f'Invalid device "{name}"')
        self.name = name


class NoInfoError(RuntimeError):
    """The device has no info from Zeroconf service"""

    def __init__(self, name: str) -> None:
        super().__init__(f'Could not find info for device "{name}"')
        self.name = name


class NotConfiguredDeviceError(RuntimeError):
    """The device is not configured"""

    def __init__(self, device_id: str, type_: str) -> None:
        super().__init__(f'Device "{device_id}" ({type_}) is not configured')
        self.id = device_id
        self.type_ = type_


class MissingDeviceKeyError(RuntimeError):
    """The device is encrypted but configuration misses the key"""

    def __init__(self, device_id: str, type_: str) -> None:
        super().__init__(f'Missing device key for encrypted device "{device_id}" ({type_})')
        self.id = device_id
        self.type_ = type_


class MissingSwitchesError(RuntimeError):
    """The device doesn't have switches"""

    def __init__(self, device_id: str, type_: str) -> None:
        super().__init__(f'Missing switches for device "{device_id}" ({type_})')
        self.id = device_id
        self.type_ = type_
