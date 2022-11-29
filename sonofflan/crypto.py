from base64 import b64decode, b64encode

from Crypto.Cipher import AES
from Crypto.Hash import MD5
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


def decrypt(data_element: str, iv: str, device_key: str) -> bytes:
    """Decrypt data from an encrypted device

    Parameters
    ----------
    `data_element` : str
        Data from the device to decrypt
    `iv` : str
        IV for the decryption
    `device_key` : str
        Encryption key for the device

    Return
    ------
    The decrypted data
    """

    dk = bytes(device_key, "utf-8")
    md5hash = MD5.new()
    md5hash.update(dk)
    key = md5hash.digest()

    cipher = AES.new(key, AES.MODE_CBC, iv=b64decode(iv))
    ciphertext = b64decode(data_element)
    padded = cipher.decrypt(ciphertext)
    plaintext = unpad(padded, AES.block_size)

    return plaintext


def encrypt(data_element: str, iv: str, device_key: str) -> str:
    """Encrypt data for an encrypted device

    Parameters
    ----------
    `data_element` : str
        Data for the device to encrypt
    `iv` : str
        IV for the encryption
    `device_key` : str
        Encryption key for the device

    Return
    ------
    The encrypted data
    """

    dk = bytes(device_key, "utf-8")
    md5hash = MD5.new()
    md5hash.update(dk)
    key = md5hash.digest()

    cipher = AES.new(key, AES.MODE_CBC, iv=b64decode(iv))
    padded = pad(bytes(data_element, "utf-8"), AES.block_size)
    ciphertext = cipher.encrypt(padded)
    encoded = b64encode(ciphertext)

    return encoded.decode("utf-8")


def generate_iv() -> str:
    """Generate IV for encrypted messages"""

    return b64encode(get_random_bytes(16)).decode("utf-8")
