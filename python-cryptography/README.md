# Python `cryptography`
This workbook is a series of working examples of software cryptography using the "de-facto standard" Python cryptography library named, appropriately, [`cryptography`](https://cryptography.io/ "The 'cryptography' library includes both high level recipes and low level interfaces to common cryptographic algorithms such as symmetric ciphers, message digests, and key derivation functions.").

> [!CAUTION]
> **DO NOT** regard the `cryptography` library's documentation examples as "safe/correct usage." They are not (and are not intended to be). They demonstrate how the API works, but in many cases they can lead to catastrophic security flaws if followed verbatim in "production" code. The examples in this workbook will clarify such cases and demonstrate the correct usage.

> [!TIP]
> Instructions in this workbook are either Bash (shell) commands or Python commands. All commands can be copied by clicking the *copy-to-clipboard* button to the right of the command block. (Instructions will hint whether to paste a copied command into a Bash command line or a Python interpreter.)

The only thing you need to complete this workbook is a working Python interpreter.  Refer to the *sdl-sw-workbooks* [README](../README.md) for various installation options for your OS.

## Workbook environment
Begin by creating and activating a Python virtual environment for this workbook.  Run each of the following three commands from a command line (terminal) on your OS (PowerShell on Windows; `bash` or `zsh` on WSL Ubuntu, macOS, or Linux).

Create the workbook virtual environment:
```console
python -m venv .venv --upgrade-deps --prompt "python-cryptography"
```

> [!WARNING]
> Activating the workbook virtual environment requires a different command based on whether you're using Windows PowerShell or `bash`/`zsh`!

Activate the workbook virtual environment on Windows PowerShell:
```console
& '.\.venv\Scripts\Activate.ps1'
```
Activate the workbook virtual environment on WSL Ubuntu/macOS/Linux:
```console
. .venv/bin/activate
```

> [!NOTE]
> Regardless of how you activate the workbook virtual environment, you should observe that your prompt now contains the prefix "(python-cryptography) " - this is your hint that the environment is currently activated.

Install the requirements using the *requirements.txt* file:
```console
python -m pip install -r requirements.txt
```

This is *rule #1* for software cryptography: **use a *trusted* cryptographic library**.
(Here "trusted" is admittedly a loaded term. The discussion is beyond the scope of this workbook, but in general we mean a library that comes from an author with reasonable credentials and that, ideally, has been publicly audited.)

## Exercise 1: Symmetric key encryption/decryption (AES in ECB mode)

Begin by entering the `python` command from your command line (terminal).  This will place you into a running Python interpreter.  (You'll know you're *in* Python because your prompt will change to `>>>`.)
```console
python
```

All commands for the remainder of this exercise are entered *directly* into your Python interpreter.

### A brief introduction to symmetric key encryption/decryption

Symmetric key encryption/decryption uses a shared "secret" key.

Our first exercise demonstrates the simplest use of symmetric key cryptography, but it also **MUST NEVER BE USED** (for reasons explained later).

First we need a random number generator (RNG). The following will import your system's best-available RNG that can be used for cryptographic purposes:
```python
from secrets import token_bytes
```
Specifically, this is a CSPRNG (i.e. a **C**ryptographically **S**ecure **P**seudo-**R**andom **N**umber **G**enerator).  It is guaranteed to be safe for use in cryptography.

> [!WARNING]
> Many languages provide RNGs as part of their standard library, but for the most part those are intended for use in simulations/games and are **UNSAFE** for cryptographic use!

We can now state *rule #2* for software cryptography: **use a verified CSPRNG for generating random bytes**.
(A corollary of this rule, which we'll encounter later: **prefer a CSPRNG provided by a *trusted* cryptographic library**.)

With our system CSPRNG imported, we can now safely generate the shared secret key:
```python
secret_key = token_bytes(16)
```
> [!WARNING]
> The shared secret key **must** be protected.  The security of the *entire system* (using symmetric encryption/decryption) relies **solely** on the secrecy of this key.  This is known as **Kerckhoffs's principle**. It is the most fundamental principle upon which symmetric encryption is based.
> 
> (In fact, in a true/real system, we wouldn't even store our secret key in a variable! We *only* do so here to simplify our examples.)

The basic building block for cryptography is called a "primitive."  In software cryptography, we typically use a "cipher," which is a generic container that can make use of a cryptographic primitive. In other words, the cipher is a software construct that performs the mathematical encryption and decryption operations.

Let's now import the `cryptography` library's [`Cipher`](https://cryptography.io/en/44.0.2/hazmat/primitives/symmetric-encryption/#cryptography.hazmat.primitives.ciphers.Cipher) class:

```python
from cryptography.hazmat.primitives.ciphers import Cipher
```

Remember, `Cipher` is generic.  We still need to tell it what *kind* of encryption/decryption to perform.  We call this an *algorithm*; an algorithm defines the mathematical details of encryption/decryption.

### The *A*dvanced *E*ncryption *S*tandard (AES)

The standard symmetric-key, block encryption algorithm is called the AES (**A**dvanced **E**ncryption **S**tandard).  It is currently based on an algorithm originally named *Rijndael*.

Import the `cryptography` library's [`AES`](https://cryptography.io/en/44.0.2/hazmat/primitives/symmetric-encryption/#cryptography.hazmat.primitives.ciphers.algorithms.AES) class:

```python
from cryptography.hazmat.primitives.ciphers.algorithms import AES
```

AES is a particular kind of cipher - a **block** cipher.  This simply means that it encrypts/decrypts in "blocks" (i.e. groups) of bytes at a time. Block ciphers have a prescribed block size. In the case of AES, the block size is 16 bytes.

Block ciphers additionally require a *mode* of operation.  The mode is a set of rules that govern how a block cipher encrypts/decrypts *multiple* blocks of bytes.

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

### The AES ECB encryption process

Our preparation is now complete; we are ready to encrypt!

We need something "confidential" to encrypt (conventionally called the *plaintext*):
```python
plaintext = "I envy Dr. Kwasa's socks.".encode("utf-8")
```
> [!TIP]
> Encryption (and decryption) is an operation performed on *bytes*.  A string variable -- such as "I envy Dr. Kwasa's socks." -- is not made up of bytes but rather of something called "glyphs" (visual symbols that represent language-specific characters).
> 
> To obtain bytes from glyphs, we need to *encode* a string using a particular "character encoding." It is important when we are encrypting/decrypting to always use the **same** character encoding to encode/decode to/from bytes. *(Failing to do so is a common defect in software cryptography!)*
> 
> For practical purposes, and unless there is a compelling reason to do otherwise, always use the UTF-8 character encoding scheme. This technique is demonstrated in the code examples that follow.

Notice that our plaintext is actually 25 bytes in length (verified by `len(plaintext)` in your Python interpreter). Clearly, 25 is not a multiple of 16. This means that we need to "pad" our plaintext *before* encrypting.

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
<a id="do-not-reuse-cipher"></a>
> [!CAUTION]
> You might be tempted to "simplify" the above expression by breaking it up into smaller pieces (as in the `cryptography` documentation, where the cipher object is created and assigned to its own variable, followed by the encryptor).
> 
> **DON'T!**
> 
> Safe/correct cryptographic usage of the `cryptography` API *requires* that the cipher object is **not** reused. More on this later (when we get to the sections on CBC and GCM modes)...

Now we use the encryptor to encrypt the (padded) plaintext.  The output is conventionally called the *ciphertext*:
```python
ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
```
> [!NOTE]
> An `encryptor` object is no longer usable after `encryptor.finalize()` has been called. This is by design.

View the ciphertext (just type `ciphertext` in the Python interpreter followed by \<Enter\>).  It should look *similar* to this:
> `b'C\x01\xbd\x9c\xf8\x1c\x9b\xa5\xd7\xff\xf7\x07\xa8k\xc2\xe3m\xd1I\xac\xd4BQ\xcd\xbeKq."\xf3+N'` 

These bytes are of no use to any party that doesn't have access to the secret key (recall **Kerckhoffs's principle**).

### The AES ECB decryption process
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

### Why ECB mode should *NEVER* be used
You did read about [The ECB Penguin](https://words.filippo.io/the-ecb-penguin/) earlier, right? If not, do so now. (This explanation of the dangers of ECB mode is regarded as *definitive*.)

If we wish to demonstrate the dangers of ECB using *our* example, specifically, that's easy to do. We only need to encrypt our (padded) plaintext again.

We need a new encryptor:
```python
encryptor = Cipher(AES(secret_key), ECB()).encryptor()
```
Now we just allow the "new" ciphertext to be printed out (rather than storing it in a variable):
```python
encryptor.update(padded_plaintext) + encryptor.finalize()
```

At this point, you can either scroll up in your terminal, or enter the variable name `ciphertext` followed by \<Enter\>. In either case, you'll notice that we got the *exact same ciphertext output*.

In cryptography, this is very, *very*, ***very*** bad. Without getting into the mathematical "proof," suffice it to say that if an adversary notices this pattern, and knows some minimum information about the nature of the plaintext being encrypted (e.g. it's in JSON format, or it contains a specific prefix), then the original plaintext can be recovered by the adversary **even *without* the secret key!**

> [!NOTE]
> A working example of the ECB weakness is provided in this workbook's supplementary materials: [Real world: Recover an AES-ECB-encrypted secret](ECB-recovery.md)

----

## Exercise 2: Symmetric key encryption/decryption (AES in CBC mode)

> [!NOTE]
> Before beginning this exercise:
>
> 1. Ensure that your "virtual environment" is activated.
> 2. Enter the Python interpreter.
>
> (Refer back to the previous section if you forget how to do #1 or #2.)

### A brief introduction to CBC mode

**Q:** If ECB mode is unsafe, what can we use instead?
**A:** CBC (Cipher Block Chaining) mode provides improved security over ECB.

Here's a simplified explanation of how CBC mode works:

1. Take the next block of plaintext bytes as input.
2. "Transform" this input plaintext block by [XOR](https://www.pcmag.com/encyclopedia/term/xor)'ing it with the *previous* ciphertext output block.
3. Encrypt this transformed plaintext block into the *next* ciphertext output block.
4. (Repeat these steps until all of the plaintext has been encrypted.)

Two things stand out in this explanation.

First, we notice how CBC mode is an improvement over ECB from step #2. Even if we encrypt the *same* plaintext multiple times, we'll get *different* ciphertext because we're transforming -- XOR'ing -- plaintext blocks before encrypting them. This effectively eliminates ECB's weakness (producing same-ciphertext-output for same-plaintext-input)!

Second, if we carefully consider step #1, we notice a problem: *When we are encrypting the **very first** block of plaintext, what are we supposed to use as the "previous ciphertext" for the XOR transformation?* To address this problem, CBC mode requires an additional piece of information called an "initialization vector."

### What is an "initialization vector" and why do we need it for CBC mode?

An **I**nitialization **V**ector (hereafter referred to simply as "IV") is a sequence of bytes that "stands in" as the first encryption round's "previous ciphertext output block" when we're using CBC mode, thus ensuring that CBC mode will produce different ciphertext blocks for *every* plaintext block (even the first one).

Important characteristics of an IV are:

1. It must be the same length as the cipher's block size.
2. It must be unique for each encryption operation.
3. it must be random. Specifically, it must be *cryptographically scure* random. (Recall our earlier discussion of PRNGs vs. CSPRNGs.)

> [!CAUTION]
> Failing to adhere to the "important characteristics of an IV" (above) compromises the security of CBC mode!
>
> Regarding characteristic #1: If the IV is *shorter* than the cipher's block size, then some information -- specifically (block size - IV length) number of bytes at the end of the first plaintext input block -- is "leaked." An adversary can use even this limited information to discover patterns.
>
> Regarding characteristic #2:
> (a) The case of an IV not being unique *in and of itself* is a special case of the previous warning. When N or more bytes of the IV are deterministic (i.e. predictable), then those same byte positions in the first ciphertext block can divulge patterns to an adversary.
> (b) The case of an IV not being unique *with respect to the secret key* is the most critical case, and is given special explanation below.
>
> Regarding characteristic #3: When we say that the IV must be random, we specifically mean that it *cannot* be based on a counter or any other "predictable" pattern, either in part or in whole.
> *Failing* to ensure the randomness of an IV is the second-most common mistake when CBC mode is incorrectly implemented.
>
> The **most** common mistake leading to incorrect CBC implementation is using the same secret-key & IV *combination* for any two encryption operations.
>
> In fact, using the same secret-key & IV to encrypt the same message (i.e. same plaintext) twice is actually $\color{red}catastrophic$ for CBC mode.
> How? (We'll answer that with an example later on in this exercise...)

### The AES CBC encryption process

All commands for the remainder of this exercise are entered *directly* into your Python interpreter.

As usual, we need a cryptographically-secure pseudo-random number generator (CSPRNG):
```python
from secrets import token_bytes
```

Regardless of mode, AES requires a shared secret key; generate a new one for this exercise:
```python
secret_key = token_bytes(16)
```

Now import the necessary `cryptography` library modules (note that we import the `CBC` module this time, instead of `ECB`):
```python
from cryptography.hazmat.primitives.ciphers import Cipher
```
```python
from cryptography.hazmat.primitives.ciphers.algorithms import AES
```
```python
from cryptography.hazmat.primitives.ciphers.modes import CBC
```
```python
from cryptography.hazmat.primitives.padding import PKCS7
```

### The AES CBC encryption process

Let's use our same "confidential" plaintext as before *(don't forget to encode as UTF-8 bytes)*:
```python
plaintext = "I envy Dr. Kwasa's socks.".encode("utf-8")
```

As with ECB mode, we need to apply padding to our input plaintext:
```python
padder = PKCS7(AES.block_size).padder()
```
```python
padded_plaintext = padder.update(plaintext) + padder.finalize()
```

Since we also know that CBC mode requires an IV, and that an IV *must* be random, let's generate one:
```python
iv = token_bytes(16)
```

To initialize a cipher for encryption in CBC mode, we need to identify the algorithm, secret key, mode, **and IV**:
```python
encryptor = Cipher(AES(secret_key), CBC(iv)).encryptor()
```
> [!CAUTION]
> Recall the [earlier caution, in the ECB mode section](#do-not-reuse-cipher), that "safe/correct cryptographic usage of the `cryptography` API *requires* that the cipher object is **not** reused?"
> 
> Notice that we specify the IV when initializing CBC mode (i.e., `CBC(iv)`). Note also our prior statement that *"using the same secret-key & IV to encrypt the same message (i.e. same plaintext) twice is actually catastrophic for CBC mode"*. Look closely at how we initialized the `encryptor` object above. If it were re-used, we'd be re-using the same IV+secret_key combination. Catastrophic! This is why we never re-use encryptor objects. We'll see a working example of the "catastrophe" later.

> [!TIP]
> Let's revisit *Kerckhoffs's principle* briefly. Recall: The security of symmetric encryption/decryption relies **solely** on the secrecy of the secret key. In other words, security does **not** depend on secrecy of the IV. In fact, not only does the IV not have to be protected, it is commonly a publically-visible value.

Now we use the encryptor to encrypt the (padded) plaintext.  The output is conventionally called the *ciphertext*:
```python
ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
```
> [!NOTE]
> An `encryptor` object is no longer usable after `encryptor.finalize()` has been called. This is by design.

View the ciphertext (just type `ciphertext` in the Python interpreter followed by \<Enter\>).  It should look *similar* to this:
> `b'C\x01\xbd\x9c\xf8\x1c\x9b\xa5\xd7\xff\xf7\x07\xa8k\xc2\xe3m\xd1I\xac\xd4BQ\xcd\xbeKq."\xf3+N'` 

These bytes are of no use to any party that doesn't have access to the secret key (recall **Kerckhoffs's principle**).

Let's now demonstrate CBC mode's advantage over ECB mode. Recall that ECB mode's weakness is that it always encrypts plaintext the same way. If we RE-encrypt the same plaintext using CBC mode (correctly, by using a new IV), we'll see that the same plaintext now encrypts to a *different* ciphertext:

```python
new_iv = token_bytes(16)
```
```python
encryptor = Cipher(AES(secret_key), CBC(new_iv)).encryptor()
```
```python
encryptor.update(padded_plaintext) + encryptor.finalize()
```

Notice that *this* ciphertext is completely different from the earlier ciphertext, even though the plaintext has not changed!

### The AES CBC decryption process
Now let's see how the ciphertext can be *decrypted* using the same secret key.

Similar to encryption, we need to initialize a cipher for *decryption*, which also requires the algorithm, secret key, and mode:
```python
decryptor = Cipher(AES(secret_key), CBC(iv)).decryptor()
```

We use the decryptor to recover our plaintext:
```python
recovered_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
```

As before, we also need to *unpad*.  Create an "unpadder" similar to how we create our padder object earlier:
```python
unpadder = PKCS7(AES.block_size).unpadder()
```

Now use the unpadder to recover our original plaintext *bytes*:
```python
original_plaintext = unpadder.update(recovered_plaintext) + unpadder.finalize()
```

Then convert these plaintext bytes (which are UTF-8 encoded) back into the original *string* value (this last command simply displays the string rather than assigning it to a variable):
```python
original_plaintext.decode("utf-8")
```

### Why IV+secret_key re-use is *catastrophic* for CBC mode

We've twice noted that *"using the same secret-key & IV to encrypt the same message (i.e. same plaintext) twice is actually catastrophic for CBC mode"*. But why is that?

Recall from our ECB mode discussion and demonstration that producing the same ciphertext for the same plaintext can allow the secret to be completely recovered **even without knowledge of the secret key**. Let's now extend this concept to CBC mode. We know that CBC mode "protects" against this case, but **only if the Isame V+secret_key combination is never re-used.** The reason that's critical is because re-using the same IV+secret!!_key combination effectively "devolves" into the ECB case!

Remember the fundamental purpose of the IV: to serve as a stand-in for the "previous" ciphertext block when we are encrypting the *first* plaintext block. Well, if we re-used the same IV with the same secret key... then we'd still get the same ciphertext for the same plaintext! And now we're right back to the problem we encountered with ECB mode!

Don't take my word for it. PROVE it to yourself:

```python
>>> encryptor = Cipher(AES(secret_key), CBC(iv)).encryptor()
```
```python
>>> encryptor.update(padded_plaintext) + encryptor.finalize()
```
Note the output ciphertext. Now repeat those same two commands again (i.e., encrypt using the same IV+secret_key). The output will be *identical*. And now we're right back to the same problem we had with ECB mode! **THIS** is why re-using the same IV+secret_key combination in CBC mode is "catastrophic" - it reduces CBC to ECB, which we've already seen is easily "breakable."

> [!NOTE]
> A working example of the CBC-with-IV-reuse weakness is provided in this workbook's supplementary materials: [Real world: Recover an AES-CBC-encrypted secret due to IV misuse](CBC-recovery.md)
