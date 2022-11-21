from sonofflan.crypto import decrypt, encrypt, generate_iv


def test_cripto():
    iv = generate_iv()
    plain = "testing text"
    key = "testing key"

    encrypted = encrypt(plain, iv, key)

    decrypted = decrypt(encrypted, iv, key)

    assert plain == decrypted.decode("utf-8")