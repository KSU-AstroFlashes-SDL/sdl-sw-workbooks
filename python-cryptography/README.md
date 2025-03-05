# Python `cryptography`
This workbook is a series of working examples of software cryptography using the "de-facto standard" Python cryptography library named, appropriately, [`cryptography`](https://cryptography.io/ "The 'cryptography' library includes both high level recipes and low level interfaces to common cryptographic algorithms such as symmetric ciphers, message digests, and key derivation functions.").

> [!WARNING]
> **DO NOT** regard the `cryptography` library's documentation examples as "safe/correct usage." They are not. They are intended to show how the API works, but in many cases they can lead to catastrophic security flaws if followed verbatim in "production" code. The examples in this workbook will clarify such cases and demonstrate the correct usage.

> [!NOTE]
> Instructions in this workbook are either Bash (shell) commands or Python commands. All commands can be copied by clicking the *copy-to-clipboard* button to the right of the command block. (Instructions will hint whether to paste a copied command into a Bash command line or a Python interpreter.)

The only thing you need to complete this workbook is a working Python interpreter.  Refer to the *sdl-sw-workbooks* [README](../README.md) for various installation options for your OS.

## Workbook environment
Begin by creating and activating a Python virtual environment for this workbook.  Run each of the following three commands from a command line (terminal) on your OS (PowerShell on Windows; `bash` or `zsh` on WSL Ubuntu, macOS, or Linux).

Create the workbook virtual environment:
```shell
python -m venv .venv --upgrade-deps --prompt "python-cryptography"
```

> [!WARNING]
> Activating the workbook virtual environment requires a different command based on whether you're using Windows PowerShell or `bash`/`zsh`!

Activate the workbook virtual environment on Windows PowerShell:
```shell
& '.\.venv\Scripts\Activate.ps1'
```
Activate the workbook virtual environment on WSL Ubuntu/macOS/Linux:
```bash
. .venv/bin/activate
```

> [!NOTE]
> Regardless of how you activate the workbook virtual environment, you should observe that your prompt now contains the prefix "(python-cryptography)" - this is your hint that the environment is currently activated.

If you cloned the *sdl-sw-workbooks* repository from GitHub, you can install the requirements using the *requirements.txt* file:
```shell
python -m pip install -r requirements.txt
```

**Alternatively,** to install the requirements manually:
```shell
python -m pip install cryptography==44.0.2
```
(Always check that this version matches what is in the *requirements.txt* file, as that is the version for which the instructions in this workbook are confirmed/tested.)

This is *rule #1* for software cryptography: **use a *trusted* cryptographic library**.
(Here "trusted" is admittedly a loaded term. The discussion is beyond the scope of this workbook, but in general we mean a library that comes from an author with reasonable credentials and that, ideally, has been publicly audited.)

## Exercise 1: Symmetric key encryption/decryption (AES in ECB mode)

Symmetric key encryption/decryption uses a shared "secret" key.

Our first exercise demonstrates the simplest use of symmetric key cryptography, but it also **MUST NEVER BE USED** (for reasons explained later).

Begin by entering the `python` command from your command line (terminal).  This will place you into a running Python interpreter.  (You'll know you're *in* Python because your prompt will change to `>>>`.)
```shell
python
```

All commands for the remainder of this exercise are entered *directly* into your Python interpreter.

First we need a random number generator (RNG). The following will import your system's best-available RNG that can be used for cryptographic purposes:
```python
from secrets import token_bytes as random_bytes
```
Specifically, this is a CSPRNG (i.e. a **C**ryptographically **S**ecure **P**seudo-**R**andom **N**umber **G**enerator).  It is guaranteed to be safe for use in cryptography.

> [!WARNING]
> Many languages provide RNGs as part of their standard library, but for the most part those are intended for use in simulations/games and are **UNSAFE** for cryptographic use!

We can now state *rule #2* for software cryptography: **use a verified CSPRNG for generating random bytes**.
(A corollary of this rule, which we'll encounter later: **prefer a CSPRNG provided by a *trusted* cryptographic library**.)

With our system CSPRNG imported, we can now safely generate the shared secret key:
```python
secret_key = random_bytes(16)
```
> [!WARNING]
> The shared secret key **must** be protected.  The security of the *entire system* (using symmetric encryption/decryption) relies **solely** on the secrecy of this key.  This is known as **Kerckhoffs's principle**. It is the most fundamental principle upon which symmetric encryption is based.
> (In fact, in a true/real system, we wouldn't even store our secret key in a variable! We *only* do so here to simplify our examples.)

The basic building block for cryptography is called a "primitive."  In software cryptography, we typically use a "cipher," which is a generic container that can make use of a specific primitive. In other words, the cipher is a software construct that performs the mathematical encryption and decryption operations.

Let's now import the `cryptography` library's [`Cipher`](https://cryptography.io/en/44.0.2/hazmat/primitives/symmetric-encryption/#cryptography.hazmat.primitives.ciphers.Cipher) class:

```python
from cryptography.hazmat.primitives.ciphers import Cipher
```

Remember, `Cipher` is generic.  We still need to tell it what *kind* of encryption/decryption to perform.  We call this an *algorithm*; an algorithm defines the mathematical details of encryption/decryption.

The standard symmetric encryption algorithm is called the AES (**A**dvanced **E**ncryption **S**tandard).  It is currently based on an algorithm originally named *Rijndael*.

Import the `cryptography` library's [`AES`](https://cryptography.io/en/44.0.2/hazmat/primitives/symmetric-encryption/#cryptography.hazmat.primitives.ciphers.algorithms.AES) class:

```python
from cryptography.hazmat.primitives.ciphers.algorithms import AES
```

AES is a particular kind of cipher - a **block** cipher.  This simply means that it encrypts/decrypts in "blocks" (i.e. groups) of bytes at a time (16 to be specific).

Block ciphers additionally require a *mode* (of operation).  The mode is a set of rules that govern how a block cipher encrypts/decrypts *multiple* blocks of bytes.

The simplest (and long-known-to-be-**UNSAFE**) mode for a block cipher is called Electronic Code Book (ECB). Exactly *why* ECB mode is unsafe is beyond the scope of this article, but we will use it here to illustrate a point.  (For the curious: read about [The ECB Penguin](https://words.filippo.io/the-ecb-penguin/).)

Import the `cryptography` library's [`ECB`](https://cryptography.io/en/44.0.2/hazmat/primitives/symmetric-encryption/#cryptography.hazmat.primitives.ciphers.modes.ECB) mode:
```python
from cryptography.hazmat.primitives.ciphers.modes import ECB
```

We're *almost* ready to encrypt, but there's one last thing we need, common to block ciphers: a *padding* scheme.

Remember earlier when we said that a block cipher encrypts/decrypts in *groups of bytes* at a time (16 for AES)? What happens if we want to encrypt something that isn't an exact multiple of 16? We need to "pad" that input until it *is* an exact multiple of 16.

As it turns out, however, we can't just "invent" our own way to pad our input, as we might inadvertently *introduce* vulnerabilities by doing so! The safe choice is to use a padding scheme that has been scrutinized by expert cryptographers and deemed acceptable for use. For AES, that "preferred" padding scheme is called PKCS#7.

Import the `cryptography` library's [`PKCS7`](https://cryptography.io/en/44.0.2/hazmat/primitives/padding/#cryptography.hazmat.primitives.padding.PKCS7) scheme:
```python
from cryptography.hazmat.primitives.padding import PKCS7
```

### The encryption process
Our preparation is now complete; we are ready to encrypt!

We need something "confidential" to encrypt (conventionally called the *plaintext*):
```python
plaintext = "I envy Dr. Kwasa's socks.".encode("utf-8")
```
> [!NOTE]
> Encryption (and decryption) is an operation performed on *bytes*.  A string variable -- such as "I envy Dr. Kwasa's socks." -- is not made up of bytes but rather of something called "glyphs" (visual symbols that represent language-specific characters).
> To obtain bytes from glyphs, we need to *encode* a string using a particular "character encoding." It is important when we are encrypting/decrypting to always use the **same** character encoding to encode/decode to/from bytes. *(Failing to do so is a common defect in software cryptography!)*
> For practical purposes, and unless there is a compelling reason to do otherwise, always use the UTF-8 character encoding scheme. This technique is demonstrated in the code examples that follow.

Notice that our plaintext is actually 25 bytes in length (verified by `len(plaintext)` in your Python interpreter). This means that we need to "pad" our plaintext *before* encrypting.

First, create a padder.  We need to provide the block size (in **bits**, not bytes) so that the padder knows the length it's padding *to*.  For AES, that's `16` (block size in bytes) * `8` (bits per byte) = `128` bits, but it's less error prone to use an API-published property for the AES block size (in bits) rather than relying on a "hard-coded" number:
```python
padder = PKCS7(AES.block_size).padder()
```

Use the padder to create the padded plaintext:
```python
padded_plaintext = padder.update(plaintext) + padder.finalize()
```
Inspection of the padded plaintext by `len(padded_plaintext)` should now show the length to be 32 bytes. This is an exact multiple of 16, suitable as input for AES encryption.

To perform an encryption operation, we need to initialize a cipher for encryption, which requires the algorithm, secret key, and mode:
```python
encryptor = Cipher(AES(secret_key), ECB()).encryptor()
```
> [!CRITICAL]
> You might be tempted to "simplify" the above expression by breaking it up into smaller pieces (as in the `cryptography` documentation, where the cipher object is created and assigned to its own variable, followed by the encryptor.
> **DON'T!**
> Safe/correct cryptographic usage of the `cryptography` API *requires* that neither the cipher nor encryptor object is reused. More on this later.

Now we use the encryptor to encrypt the (padded) plaintext.  The output is conventionally called the *ciphertext*:
```python
ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
```
> [!NOTE]
> An `encryptor` object is no longer usable after `encryptor.finalize()` has been called. This is by design.

View the ciphertext (just type `ciphertext` in the Python interpreter followed by \<Enter\>).  It should look *similar* to this:
> `b'C\x01\xbd\x9c\xf8\x1c\x9b\xa5\xd7\xff\xf7\x07\xa8k\xc2\xe3m\xd1I\xac\xd4BQ\xcd\xbeKq."\xf3+N'` 

These bytes are of no use to any party that doesn't have access to the secret key (recall **Kerckhoffs's principle**).

### The decryption process
Now let's see how the ciphertext can be *decrypted* using the same secret key.

Similar to encryption, we need to initialize a cipher for *decryption*, which also requires the algorithm, secret key, and mode:
```python
decryptor = Cipher(AES(secret_key), ECB()).decryptor()
```

We use the decryptor to recover our plaintext:
```python
recovered_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
```

But remember - our plaintext is *padded!* So after decryption, we also need to *unpad*.  Create an "unpadder" similar to how we create our padder object earlier:
```python
unpadder = PKCS7(AES.block_size).unpadder()
```

Now use the unpadder to recover our original plaintext *bytes*:
```python
original_plaintext = unpadder.update(recovered_plaintext) + unpadder.finalize()
```

Finally, recall the previous note about "character encoding." We need to convert these plaintext bytes (which are UTF-8 encoded) back into the original *string* value (this last command simply displays the string rather than assigning it to a variable):
```python
original_plaintext.decode("utf-8")
```

## Why ECB mode should *NEVER* be used
You did read about [The ECB Penguin](https://words.filippo.io/the-ecb-penguin/) earlier, right? If not, do so now. (This explanation of the dangers of ECB mode is regarded as *definitive*.)

If we wish to demonstrate the dangers of ECB using *our* example, specifically, that's easy to do. We only need to encrypt our (padded) plaintext again.

We need a new encryptor:
```python
encryptor = Cipher(AES(secret_key), ECB()).encryptor()
```
Now we just allow the "new" ciphertext to be printed out (rather than storing it in a variable):
```python
encryptor.update(plaintext) + encryptor.finalize()
```
At this point, you can either scroll up in your terminal, or enter the variable name `ciphertext` followed by \<Enter\>. In either case, you'll notice that we got the *exact same ciphertext output*.

In cryptography, this is very, *very*, ***very*** bad. Without getting into the mathematical "proof," suffice it to say that if an adversary notices this pattern, and knows some minimum information about the nature of the plaintext being encrypted (e.g. it's in JSON format, or it contains a specific prefix), then the original plaintext can be recovered by the adversary **even *without* the secret key!**

