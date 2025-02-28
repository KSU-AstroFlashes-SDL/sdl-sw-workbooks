# Python `cryptography`
This workbook is a series of working examples of software cryptography using the de-facto "standard" Python cryptography library named, appropriately, [`cryptography`](https://cryptography.io/ "The 'cryptography' library includes both high level recipes and low level interfaces to common cryptographic algorithms such as symmetric ciphers, message digests, and key derivation functions.").

> [!NOTE]
> Instructions in this workbook are either Bash (shell) commands or Python commands. All commands can be copied by clicking the *copy-to-clipboard* button to the right of the command block. (Instructions will hint whether to paste a copied command into a Bash command line or a Python interpreter.)

> [!WARNING]
> Many code blocks contain multiple lines. It is generally advisable to **not** use the *copy-to-clipboard* button in these cases.  (Since these are intended as live exercise, such blocks should be copied and pasted one at a time.)

## Workbook environment
Begin by creating and activating a Python virtual environment for this workbook.  Run each of the following three commands from a `bash` or `zsh` shell.

Create the virtual environment:
```bash
python -m venv .venv --upgrade-deps --prompt "$(basename $(pwd))"
```

Activate the virtual environment (don't miss the "dot" character):
```bash
. .venv/bin/activate
```

Install the requirements:
```bash
python -m pip install -r requirements.txt
```

## Exercise 1: Symmetric key encryption/decryption

Symmetric key encryption/decryption uses a shared "secret" key.

Our first example is the simplest, but it also MUST NEVER BE USED (for reasons explained later).

All of these commands are entered directly into a Python interpreter.

First we need to import the things we'll need:
```python
from secrets import token_bytes as random_bytes
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
```

To encrypt/decrypt anything, we'll need a random key.
```python
secret_key = random_bytes(16)
```

We need something "secret" to encrypt.  This is conventionally called the "plaintext."
```python
plaintext = "I wish my socks were as in-vogue as Dr. Kwasa's!"
```

Now we encrypt the plaintext.  The output is conventionally called the "ciphertext."
```python
cipher = Cipher(AES(secret_key), ECB())
encryptor = cipher.encryptor()
ciphertext = encryptor.update(plaintext) + encryptor.finalize()
```

Take a look at the ciphertext (just type the variable name in the Python interpreter followed by \<Enter\>).  It should look something like this: `b'\x9d\x119e4&\xa1\x81\x07H+o\x13\xde\x8eBn\xdfZ\x974\x1e\xd8\xd3>\xa3(\x95\x10l\xd0\xca\x1e\x12\x92\x8c\xd7q\x80\xfe\xcc/\xf2\x87\x035\xe2\xa7'`

This string of bytes is of no use to any party that doesn't have the secret key.

Now observe that the ciphertext can be decrypted using the secret key.  (The last command in this sequence will output the decrypted plaintext directly to the screen.)
```python
cipher = Cipher(AES(secret_key), ECB())
decryptor = cipher.decryptor()
decryptor.update(ciphertext) + decryptor.finalize()
```

