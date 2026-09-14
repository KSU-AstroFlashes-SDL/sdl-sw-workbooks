"""
Demonstration: catastrophic failure of AES-GCM under (key, nonce) reuse.

Two independent failures are shown:
  1. Keystream reuse -> XOR of ciphertexts reveals XOR of plaintexts.
     This requires ONLY that (key, nonce) repeat. AAD is irrelevant here.
  2. Crib-drag plaintext recovery -> if the attacker knows ONE plaintext,
     they recover the OTHER plaintext with no knowledge of the key at all.

A third failure (the "forbidden attack": full recovery of the GHASH
authentication subkey H, enabling universal tag forgery) is described
but not implemented here, because it additionally requires the two
messages to share the SAME associated data (AAD) length/content
handling; it is a separate, more involved derivation from the two
(ciphertext, tag) pairs and the shared H-polynomial evaluation.
"""

from secrets import token_bytes

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


if __name__ == "__main__":
    secret_key = token_bytes(32)
    cipher = AESGCM(secret_key)

    # VULNERABILITY: same nonce used for two different encryption operations
    # with the same secret_key. This must NEVER happen with GCM!
    nonce = token_bytes(12)

    # it doesn't matter that we use different AAD for each encryption -
    # the vulnerability still works
    plaintext1 = input("Enter plaintext #1: ")
    plaintext1_bytes = plaintext1.encode("utf-8")
    ctmac1 = cipher.encrypt(nonce, plaintext1_bytes, b"test1")

    plaintext2 = input("Enter plaintext #2: ")
    plaintext2_bytes = plaintext2.encode("utf-8")
    ctmac2 = cipher.encrypt(nonce, plaintext2_bytes, b"test2")

    # just to prove that the vulnerability requires ZERO knowledge of the
    # secret key, we'll destroy it AND the cipher before continuing
    secret_key = None
    del secret_key
    cipher = None
    del cipher

    # we assume that the adversary can "know" ctmac1 and ctmac2
    # (e.g., perhaps they can eavesdrop on network comms)
    ciphertext1, mac1 = ctmac1[:-16], ctmac1[-16:]
    ciphertext2, mac2 = ctmac2[:-16], ctmac2[-16:]

    # this is critical - it means that the adversary doesn't need to know the
    # keystream AT ALL! It cancels out because GCM used the same keystream for
    # both operations because of (secret_key, nonce) re-use!
    # i.e., ct1 ^ ct2 = (pt1 ^ ks) ^ (pt2 ^ ks) = pt1 ^ pt2
    ciphertext_xor = xor_bytes(ciphertext1, ciphertext2)
    plaintext_xor = xor_bytes(plaintext1_bytes, plaintext2_bytes)
    assert ciphertext_xor == plaintext_xor
    print("Same (secret_key, nonce) -> same GCM keystream")

    # the practical application of the above is that if the adversary can know
    # (or successfully guess) ONE of the plaintexts, then they can recover the
    # OTHER plaintext WITHOUT any knowledge of the secret key!
    print("I can recover either of your plaintexts if I know (or can guess) *one* of them!")
    print("Which plaintext should I know (or successfully guess)?")
    print(f"1) {plaintext1!r}")
    print(f"2) {plaintext2!r}")
    choice = None
    while (choice := input("Enter 1 or 2: ")) not in ['1', '2']:
        continue
    known_or_guessed_plaintext = plaintext1 if choice == '1' else plaintext2

    recovered_plaintext = xor_bytes(ciphertext_xor, known_or_guessed_plaintext.encode("utf-8"))
    print("I receovered the other plaintext WITHOUT the secret key:")
    print(f"{recovered_plaintext.decode('utf-8')!r}")

