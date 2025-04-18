import os
from secrets import token_bytes

from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import ECB
from cryptography.hazmat.primitives.padding import PKCS7

__all__ = ["encrypt", "decrypt"]

# demo only
SKEY_FN = ".skey.bin"


def encrypt(plaintext: bytes) -> bytes:
    pt = _padded(plaintext)
    with open(SKEY_FN, "rb") as key:
        encryptor = Cipher(AES(key.read()), ECB()).encryptor()
    return encryptor.update(pt) + encryptor.finalize()


def _padded(plaintext: bytes) -> bytes:
    padder = PKCS7(AES.block_size).padder()
    return padder.update(plaintext) + padder.finalize()


def decrypt(ciphertext: bytes) -> bytes:
    with open(SKEY_FN, "rb") as key:
        decryptor = Cipher(AES(key.read()), ECB()).decryptor()
    pt = decryptor.update(ciphertext) + decryptor.finalize()
    return _unpadded(pt)


def _unpadded(pt: bytes) -> bytes:
    unpadder = PKCS7(AES.block_size).unpadder()
    return unpadder.update(pt) + unpadder.finalize()


# ensure we always have a secret key
if not os.path.isfile(SKEY_FN):
    # only accessible to the owner
    fd = os.open(SKEY_FN, os.O_CREAT | os.O_WRONLY, 0o600)
    try:
        os.write(fd, token_bytes(32))   # 256-bit key
    finally:
        os.close(fd)

