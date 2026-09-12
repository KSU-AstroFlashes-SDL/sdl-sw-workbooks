import os
from secrets import token_bytes

from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.padding import PKCS7

__all__ = ["decrypt", "encrypt"]

# demo only
SECRET_KEY = "secret_key.bin"

# This is the "catastrophic" misuse of AES in CBC mode - a re-used IV.
# In the real-life case that inspired this exercise, the vendor had wanted a
# "simplified" encryption/decryption API that accepted only the plaintext or
# ciphertext bytes, respectively. The developer who implemented the API, not
# understanding the purpose of an IV, simply generated the IV once and stored
# the value for reuse, thus introducing the security defect.
#
# CHALLENGE:
# Can you think of a *better* way to implement this API *without* breaking
# backwards compatibility?
# In other words... Can you think of a way to keeep the encrypt(bytes) -> bytes
# and decrypt(bytes) -> bytes function signatures while AVOIDING reuse of the
# same IV?
# (The answer to this challenge is actually the most common real-world
# implementation of AES-CBC that is "correct.")
# HINTS:
# * Remember that Kerckhoff's principle implies that the IV is public
#   knowledge.
# * The correct solution is actually imlied by the make-admin-cbc.py script's
#   "help" message.
VENDOR_IV = b"\xe3\xd8\xd0-\xec~\xdevr\xd8`[\x8cz\x8fd"


def encrypt(plaintext: bytes) -> bytes:
    pt = _padded(plaintext)
    with open(SECRET_KEY, "rb") as key:
        encryptor = Cipher(AES(key.read()), CBC(VENDOR_IV)).encryptor()
    return encryptor.update(pt) + encryptor.finalize()


def _padded(plaintext: bytes) -> bytes:
    padder = PKCS7(AES.block_size).padder()
    return padder.update(plaintext) + padder.finalize()


def decrypt(ciphertext: bytes) -> bytes:
    with open(SECRET_KEY, "rb") as key:
        decryptor = Cipher(AES(key.read()), CBC(VENDOR_IV)).decryptor()
    pt = decryptor.update(ciphertext) + decryptor.finalize()
    return _unpadded(pt)


def _unpadded(pt: bytes) -> bytes:
    unpadder = PKCS7(AES.block_size).unpadder()
    return unpadder.update(pt) + unpadder.finalize()


# ensure we always have a secret key
if not os.path.isfile(SECRET_KEY):
    # only accessible to the owner
    fd = os.open(SECRET_KEY, os.O_CREAT | os.O_WRONLY, 0o600)
    try:
        os.write(fd, token_bytes(32))  # 256-bit key
    finally:
        os.close(fd)
