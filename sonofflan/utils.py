def parse_address(address: bytes):
    """Resolve the IP address of the device"""

    address_list = []
    for i in range(4):
        address_list.append(int(address.hex()[(i * 2): (i + 1) * 2], 16))
    return f"{address_list[0]}.{address_list[1]}.{address_list[2]}.{address_list[3]}"
