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

CBC (Cipher Block Chaining) mode provides improved security over ECB.

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

----

## Interlude: Authenticity: What is it and why do I care?

Until now, we've only concerned ourselves with one aspect of data security: *confidentiality*. In cryptography, this is the "guarantee" that sensitive data is only retrievable by parties that possess the secret key (for symmetric key algorithms like AES).

But there's another concern that is arguably just as important: *authenticity*. In other words, how do I know that these ciphertext bytes I've received have not been corrupted (or worse, forged)?

An encryption algorithm like AES does not concern itself with authenticity; its job is to ensure confidentiality only. This means that authenticity needs to be implemented as a separate step.

In traditional practice, a process called "encrypt-then-sign" was used to guarantee both confidentiality and authenticity. The "encrypt-then-sign" process is as follows:

1. Sender provides or publishes their asymmetric PUBLIC key.
2. Sender & receiver agree on a symmetric (shared) secret key.
3. Sender encrypts sensitive data using the symmetric (shared) secret key.
4. Sender digitally signs the ciphertext using their asymmetric PRIVATE key.
5. Sender conveys the signature+ciphertext to the receiver.
6. Receiver verifies the signature using the sender's provided/published asymmetric PUBLIC key.
7. IF the signature passes verification, THEN receiver decrypts sensitive data using the symmetric (shared) secret key, ELSE receiver discards the data.
   (Importantly, in the "ELSE" case, receiver never performs decryption because the data either is garbage or, in the case of forgery, dangerous.)

This is a reliable, proven process for sharing sensitive data, but notice that it requires a non-insignificant amout of overhead. The sender and receiver must agree upon (i.e., share) TWO different keys: the sender's asymmetric PUBLIC key *and* the symmetric (shared) secret key.
And the sharing of a symmetric secret key is a process that *itself* must be secured! In fact, sharing of symmetric secret keys is an entire field of research in its own right!
(For the curious: see
[Diffie-Hellman key exchange](https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange),
one of the oldest key-sharing mechanisms still in use.)

But what if we could somehow simplify confidentiality+authenticity? As it turns out, we can.

### Authenticated Encryption (with Associated Data)

**AE** ([**A**uthenticated **E**ncryption](https://en.wikipedia.org/wiki/Authenticated_encryption)) is an encryption scheme that *simultaneously* ensures data confidentiality (by encryption) and data authenticity (by signing).
(In contrast, AES-CBC is a non-AE scheme that provides *only* data confidenitality by encryption; you'd need to "manually" sign the encrypted data in a separate step to be able to assert its authenticity.)

**AEAD** is
[**A**uthenticated **E**ncryption _with **A**ssociated **D**ata_](https://en.wikipedia.org/wiki/Authenticated_encryption#Authenticated_encryption_with_associated_data).
This scheme allows you to associate *unencrypted* data with the encrypted data while verifying the authenticity of *both* (as a unit). The canonical example is a network packet where the header data needs to remain unencrypted but the *combination* of unencrypted headers and encrypted payload should be verified as a unit. So you'd verify the digital signature (cryptographic hash) of the headers+payload and only *then* would you decrypt the payload. (Otherwise you'd discard it.)

AEAD is the preferred encryption/decryption mechanism in the modern day, precisely because of the combined confidentiality+authenticity mechanism. Many modern software cryptography libraries take this one step further, abstracting (hiding) *all* of the details of cipher setup and initialization behind a simplified API that attempts to make misuse impossible (or at least difficult). Such APIs are beyond the scope of this workbook, as our purpose here is to teach basic concepts.

Two prominent AEAD constructions are AES-GCM and ChaCha20-Poly1305, covered in the final two exercises below.

----

## Exercise 3: Symmetric key AEAD encryption/decryption (AES in GCM mode)

**GCM** (**G**alois **C**ounter **M**ode) is a block cipher mode that implements the AEAD scheme.
Thus, AES-GCM gives us the confidentiality guaranteed by AES along with the authenticity guarantee of a Message Authentication Code (MAC).

> [!NOTE]
> A MAC (Message Authentication Code) is more than just a hash, but it's also different from a digital signature.
>
> In short:
> * A hash doesn't require a key at all. It just produces a unique "fingerprint" for some input.
> * A MAC (Message Authentication Code) is also a unique "fingerprint" (for the ciphertext), but it **requires** use of the symmetric secret key. So, a MAC can only be computed (and verified) by a party that is in possession of the symmetric secret key.
> * A Digital Signature is *also* a unique "fingerprint" (for the ciphertext), but is is implemented by an *asymmetric* key pair (i.e., a private and public key pair). A digital signature can only be calculated by the owner of the private key, but anyone in possession of the public key can verify such a signature.
>   (Asymmetric algotithms are beyond the scope of this workbook, although we'll mention them again briefly later in this section.)

### A brief introduction to GCM mode (an AEAD scheme)

Just as CBC mode requires an IV, GCM mode requires a **nonce** (a "**n**umber used **once**").

> [!NOTE]
> The difference between an *IV* and a *nonce* is subtle but important.
>
> Both IVs and nonces must be *unique* in combination with a given secret key. In other words, our earlier claim that (key, IV) pairs should be unique for every encryption operation ALSO holds true for (key, nonce) pairs.
>
> The *difference* between IV and nonce (specifically, the difference between an IV used in CBC mode versus a nonce used in GCM mode) is that the CBC IV **must** be unpredictable, while the GCM nonce only needs to be **unique** (with respect to the key).
> For CBC IVs, the "unpredictability" requirement is most commonly met by generating a random IV using a CSPRNG. For GCM nonces, believe it or not, the *ideal* mechanism is to use a simple counter (1, 2, 3, ..., 2**96) since that satisfies the uniqueness requirement using the entire 96-bit space (GCM nonces are 96 bits, or 12 bytes).

> [!CAUTION]
> While it might seem tempting to use a "simple" 96-bit counter for GCM mode, there are some practical implications that make this approach uncommon.

> For starters, such a counter implementation MUST use some kind of persistent storage to keep track of the last-used counter value. This is actually much harder to implement in practice than you might think!
>
> In practice, we typically see AES-GCM implementation using a CSPRNG to produce a random 12-byte (96-bit) nonce precisely because this operation is stateless. But it comes with its own warning: a weakness known as the [Birthday attack](https://en.wikipedia.org/wiki/Birthday_attack) means that we can only safely generate a "unique" (random) nonce for a maximum of 2**48 (281,474,976,710,656) messages before we'd need to generate a new symmetric secret key.

All commands for the remainder of this exercise are entered *directly* into your Python interpreter.

As usual, we need a cryptographically-secure pseudo-random number generator (CSPRNG):
```python
from secrets import token_bytes
```

Regardless of mode, AES requires a shared secret key; generate a new one for this exercise:
```python
secret_key = token_bytes(16)
```

> [!NOTE]
> Before beginning this exercise:
>
> 1. Ensure that your "virtual environment" is activated.
> 2. Enter the Python interpreter.
>
> (Refer back to the first section if you forget how to do #1 or #2.)

Now import the necessary `cryptography` library module. **Unlike previous sections**, for AES GCM notice that we import a combined cipher+mode class `AESGCM` (instead of importing `Cipher`, the `AES` alogithm, and `GCM` mode separately). This usage protects against some accidental misuses:
```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
```

> [!NOTE]
> Do you notice an omission from the imports?
>
> *We do NOT import the PCKS7 padding module for GCM mode.* Why?
> GCM effectively turns AES into what is known as a "stream cipher." Unlike block ciphers, which operate on a prescribed number of *blocks* of bytes, stream ciphers operate on a single byte at a time. So, for GCM mode, ciphers operate on a single byte at a time and so padding is not required.
>
> There *are* cases in which padding the input might be desirable even in GCM mode, but even then PKCS7 is emphatically the *wrong* choice. That discussion is beyond the scope of this workbook, though.

### The AES GCM encryption process

Let's use our same "confidential" plaintext as before *(don't forget to encode as UTF-8 bytes)*:
```python
plaintext = "I envy Dr. Kwasa's socks.".encode("utf-8")
```

Since we also know that GCM mode requires a **unique** 96-bit (12-byte) nonce, let's generate one (noting the caveat about random nonces from earlier):
```python
nonce = token_bytes(12)
```

Let's also choose some "*a*dditional *a*ssociated *d*ata" (the **AD* in **AEAD**) so that we can demonstrate the full API. Remember *Kerckhoff's principle* - our AD is **not** secret.
Also remember our rule about character encoding: we always encode strings to UTF-8, because cryptographic APIs deal with *bytes*, not strings.
```python
aad = "workbook example".encode("utf-8")
```

We're ready to encrypt, so let's first create our AES GCM cipher, and then perform the encryption operation:
```python
cipher = AESGCM(secret_key)
```
```python
ciphertext_and_mac = cipher.encrypt(nonce, plaintext, aad)
```

> [!TIP]
> This usage differs significantly from what we saw earlier for ECB and CBC modes.
>
> Most notably, this usage is much simpler. That's by design. It's a tendency of modern cryptographic libraries to apply such simplifications in order to avoid (or at least "steer away from") common misuse of cryptographic APIs.
>
> In this case, notice that the API of `AESGCM` reinforces the idea that a (key, nonce) pair should not be re-used by removing the nonce from the cipher initialization and placing it instead with the `encrypt()` method arguments.
> Notice also that our return value is no longer *just* the ciphertext - it's the ciphertext *with the MAC appended*.
>
> A convenient side effect of this design is that we **can** now reuse the `cipher` object we created because it is only associated with the secret key.

Recall from an earlier section that AEAD constructions (such as AES GCM) automatically calculate a Message Authentication Code (MAC). You may have been wondering how we make use of that MAC. The previous command to encrypt our plaintext should give you a hint. Notice that the value returned by the `encrypt()` method is **not** just the ciphertext - it's the concatenation of the MAC *and* ciphertext. This is one of the hallmarks of AEAD constructions. When we send the encrypted message to a recipient, we always send *both* the MAC and ciphertext (because the recipient needs to be able to perform the MAC verification so that they can assert the authenticity of the message).

View the ciphertext (just type `ciphertext_and_mac` in the Python interpreter followed by \<Enter\>).  It should look *similar* to this:
> `b'_8\x8bJ!\xbb $g\xec\xf6s\xf3\xdb\xf5\x96\x89\xe4W\xb3/{ZL\xc6w\x90\x17"\x08\x95\x8aQ9\x930]\x8c=\x12:'`

There are more bytes here than in `b"I envy Dr. Kwasa's socks."`. How many more, exactly?
```python
len(ciphertext_and_mac) - len(plaintext)
```
You should see that the difference is `16` - i.e., the length of an AES GCM MAC!

Usually at this point the workbook would point out the danger of re-using the same nonce with the same key. We're going to hold off on that discussion until later, after we've covered AES GCM decryption, because there's a suprise in store...

### The AES GCM decryption process
Now let's see how the ciphertext can be *decrypted* using the same secret key and nonce, and *verified* using the MAC.

**Unlike previous examples using ECB and CBC modes**, here we can safely re-use our `cipher` instance (as noted above).

Since we already have our nonce and *aad*, we can decrypt directly. But first, let's see first hand how MAC verification asserts the authenticity of our message.

There are three cases where MAC verification can fail:
1. The ciphertext has been corrupted/forged before the recipient receives the message.
2. The MAC itself has been corrupted/forged before the recipient receives the message.
3. The recipient uses the wrong "associated data" when decrypting. (Or doesn't specify it at all.)

**Case #1**
Here we'll just prepend a single byte of "garbage data" to the ciphertext so that the recipient's calculated MAC won't match the message MAC:
```python
cipher.decrypt(nonce, b"Z" + ciphertext_and_mac, aad)
```
This **should** fail due to `cryptography.exceptions.InvalidTag`.

**Case #2**
This is a bit more complicated to force-fail, because we can't simply append a "garbage byte" to the MAC (it **must** be exactly 16 bytes in length). Instead, we'll just change a single byte of the MAC.
The next three commands change the last byte of the MAC to a different byte value.
```python
last_mac_byte = ciphertext_and_mac[-1]
```
```python
bad_mac_byte = last_mac_byte - 1 if last_mac_byte > 0 else 0
```
```python
ciphertext_and_bad_mac = ciphertext_and_mac[:-1] + bad_mac_byte.to_bytes()
```
At this point, you can simply type `ciphertext_and_mac` followed by \<Enter\> and then `ciphertext_and_bad_mac` followed by \<Enter\> to see both values on your screen. It should be visibly apparent that the LAST byte of each is different.
Finally, attempt the decryption:
```python
cipher.decrypt(nonce, ciphertext_and_bad_mac, aad)
```
Again, this **should** fail due to `cryptography.exceptions.InvalidTag`.

**Case #3**
Here we'll use a different value for *aad* (literally):
```python
cipher.decrypt(nonce, ciphertext_and_mac, b"different value")
```
Yet again, this **should** fail due to `cryptography.exceptions.InvalidTag`.

Finally, we'll perform the decryption operation expecting success:
```python
recovered_plaintext = cipher.decrypt(nonce, ciphertext_and_mac, aad)
```
And don't forget to turn our plaintext back into a string!
```python
recovered_plaintext.decode("utf-8")
```
This last command should produce `"I envy Dr. Kwasa's socks."`, as intended.

### GCM mode and secret_key+nonce re-use

Earlier we learned that secret_key+IV re-use for CBC mode is *catastrophic*. We saw first hand how we could recover an encrypted secret, even without knowing the key, just because we re-used the same (secret_key, IV) pair.

Do we get the same catastrophic result if we re-use the same (secret_key, nonce) pair in GCM mode?

Well, recall that our "signal" of a re-used (secret_key, IV) pair in CBC mode was that we got the *same* ciphertext when encrypting the same plaintext. Does the same thing happen in GCM mode?
```python
cipher.encrypt(nonce, plaintext, aad)
```
This will display the ciphertext (and MAC) directly on your screen. If you scroll up in your terminal, you should be able to visually confirm that you got the exact same result. This would seem to confirm, based on our prior observations and tests, that re-using the same (secret_key, nonce) pair is also catastrophic for GCM. **Spoiler alert: YES, it is catastrophically bad to re-use the same (secret_key, nonce) pair in GCM mode.**

> [!CAUTION]
> What you might *not* expect is that (secret_key, nonce) re-use in GCM mode is **even MORE catastrophic** than (secret_key, IV) re-use in CBC mode!
>
> This is because an adversary that can acquire ANY two ciphertexts (and their MACs) where the same (secret_key, nonce) was used can gain the ability to forge ciphertexts *and* MACs! The resulting forgeries will be **undetectable**!
> For example, an adversary could forge a message that instructs your banking system to transfer all funds into another account (of the adversary's choosing). Your system will happily act on that message because it will believe it to be valid (it will pass MAC verification).
> (For the interested, see [Why AES-GCM Sucks: GHASH Brittleness](https://soatok.blog/2020/05/13/why-aes-gcm-sucks/#ghash).)

The vulnerability described above is far beyond the scope of this workbook as it involves calculating roots of polynomial equations (too much for a quick demo, but very feasible for a determined adversary).

However, another weakness is much easier to demonstrate: (secret_key, nonce) reuse in GCM mode also allows for plaintext recovery under certain conditions.

Try a quick test:
```python
ctmac1 = cipher.encrypt(nonce, b"I envy Dr. Kwasa's socks.", b"test1")
```
```python
ctmac2 = cipher.encrypt(nonce, b"Spam and eggs are delicious.", b"test2")
```
Here we're simulating use of the same (secret_key, nonce) pair, but as might be expected for two different messages, we've changed both the plaintext and the associated data.
Display both outputs on your screen by typing `ctmac1` then \<Enter\> followed by `ctmac2` then \<Enter\>.
The outputs should be *completely* different.

So we're "safe" in thise case, even though we re-used the same (secret_key, nonce) pair, right?

**NO!!!** Re-using (secret_key, nonce) compromises GCM *completely*. For example, if an adversary knows (or can guess) ONE plaintext, then another can be recovered if the same (secret_key, nonce) pair was used for encryption. Try the following working example to see it in action:

1. Exit your Python interpreter (\<Ctrl\>-Z then \<Enter\> on Windows, or \<Ctrl\>-D on Mac/Linux).
2. At the command prommpt, run `python gcm-nonce-reuse-recover-plaintext.py`
3. When prompted for plaintext #1, type "I envy Dr. Kwasa's socks." (without quotes) then press \<Enter\>.
4. When prompted for plaintext #2, type "Spam and eggs are delicious." (without quotes) then press \<Enter\>.
5. When prompted to choose which plaintext is known/guessed, type "2" (without quotes) then press \<Enter\>.

Enjoy (or be shocked by) the result: the program can guess the other plaintext with **no knowledge of the secret key**!
Open `gcm-nonce-reuse-recover-plaintext.py` in an editor (or view it in this project on GitHub) and read through the comments for more details of the vulnerability.

> [!TIP]
> Try the example again, but this time choose "1" for the known/guessed plaintext.
>
> What happens? Can you explain why? (Hint: XOR, which is used in the recovery logic, is a *binary* operation - it requires TWO inputs.)

----

## Exercise 4: Symmetric key AEAD encryption/decryption (ChaCha20-Poly1305)

In the previous exercise, we noted that GCM mode, applied to AES, "effectively" turns AES (a block cipher) *into* a stream cipher.

ChaCha20 is a stream cipher by design. It is typically paired with Poly1305, a MAC (Message Authentication Code) scheme, to create another AEAD construction.

While AES-GCM and ChaCha20-Poly1305 are both AEAD constructions, they differ in three important ways:

1. ChaCha20-Poly1305 has a variant - XChaCha20-Poly1305 (note the "X") - that uses a MUCH larger nonce (192 bits instead of 96) to reduce the likelihood of same (secret_key, nonce) collisions when using a random nonce. Notably, both AES-GCM *and* ChaCha20-Poly1305 (under random nonce generation) have a practical message limitation of 2**48 messages, while **X**ChaCha20-Poly1305 is reported to have "no practical limitation." (ref https://www.pycryptodome.org/src/cipher/chacha20).
2. Poly1305 generates a **new** MAC-calculation key for each message (unlike AES-GCM, which derives the same MAC-calculation key for a given AES secret key.)
3. AES-GCM is NIST-approved, while (X)ChaCha20-Poly1305 is not. *This matters if your software requirements call for a NIST-compliant AEAD construction!*

Both ChaCha20-Poly135 and AES-GCM are in widespread use, but the points above are important considerations based on project software requirements.

> [!NOTE]
> Before beginning this exercise:
>
> 1. Ensure that your "virtual environment" is activated.
> 2. Enter the Python interpreter.
>
> (Refer back to the first section if you forget how to do #1 or #2.)

> [!NOTE]
> The Python `cryptography` library, which we are using in this workbook, **does not support** the "X" variant of ChaCha20-Poly1305, so in this exercise we are using a 96-bit (12-byte) nonce.

As usual, we need a cryptographically-secure pseudo-random number generator (CSPRNG):
```python
from secrets import token_bytes
```

Next import `ChaCha20Poly1305`:
```python
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
```

We always need a shared secret key, so generate a new one for this exercise (note that ChaCha20 uses a 32-byte key:
```python
secret_key = token_bytes(32)
```

### The ChaCha20-Poly1305 encryption process

We'll use our usual "confidential" plaintext:
```python
plaintext = "I envy Dr. Kwasa's socks.".encode("utf-8")
```

ChaCha20 requires a **unique** 96-bit (12-byte) nonce, again noting the caveat about random nonces from earlier (and **X**ChaCha20's improved 192-bit nonce):
```python
nonce = token_bytes(12)
```

Let's also choose our "*a*dditional *a*ssociated *d*ata" so that we can demonstrate the full API:
```python
aad = "workbook example".encode("utf-8")
```

We're ready to encrypt, so let's first create our cipher, and then perform the encryption operation:
```python
cipher = ChaCha20Poly1305(secret_key)
```
```python
ciphertext_and_mac = cipher.encrypt(nonce, plaintext, aad)
```

Since ChaCha20 is a stream cipher, we can easily discover the MAC length (it's 16):
```python
len(ciphertext_and_mac) - len(plaintext)
```

> [!CAUTION]
> The same warning applies for ChaCha20-Poly1305 as for AES-GCM: **do not reuse (secret_key, nonce) pairs!***
> (more on this later...)

### The ChaCha20-Poly1305 decryption process
Now let's see how the ciphertext can be *decrypted* using the same secret key and nonce, and *verified* using the MAC.

As with `AESGCM`, here we can safely re-use our `cipher` instance.

Since we already have our nonce and *aad*, we can decrypt directly. (We could also examine MAC verification failures in the same way we did for AES-GCM, but we skip it here for brevity.)

```python
recovered_plaintext = cipher.decrypt(nonce, ciphertext_and_mac, aad)
```
And don't forget to turn our plaintext back into a string!
```python
recovered_plaintext.decode("utf-8")
```
This last command should produce `"I envy Dr. Kwasa's socks."`, as intended.

### ChaCha20-Poly1305 and secret_key+nonce re-use

As noted above, ChaCha20-Poly1305 is still susceptible to nonce-reuse vulnerability, with one main difference as compared to AES-GCM: the "GHASH Brittleness" vulnerability does **not** apply to ChaCha20-Poly1305 because the latter does not use the GHASH mechanism to determine the MAC calculation key.

However, ChaCha20-Poly1305 **IS** still vulnerable to the exploit detailed in `gcm-nonce-reuse-recover-plaintext.py` (just with `ChaCha20Poly1305` as the cipher instead of `AESGCM` of course).

> [!TIP]
> As an optional exercise, you can make a copy of `gcm-nonce-reuse-recover-plaintext.py`, rename it (to something like `ccpoly-nonce-reuse-recover-plaintext.py`), and confirm for yourself that the vulnerability still exists with ChaCha20-Poly1305.

----

## Summary

**Caongratulations!**

If you made it all the way through this workbook, it is fair to say that you know more about software cryptography than *most* developers! (Or at least you're more *aware* of software cryptography practices than most developers!)

This is no small thing! But as with most endeavors, there's MUCH more to learn if you have the interest and motivation. (And, truthfully, I've made a great many simplifications in this workbook - and probably introduced some errors in terminology/conceptualization along the way.)

If you remember none of the detail in this workbook, I hope you at least come away understanding # things:

1. **Your system's security is only as strong as its WEAKEST link.**
2. The weakest link is seldom the encryption *algorithm* you choose (assuming you've chosen one that is vetted and "approved" by the cryptography community)
3. The weakest link **CAN** be:
   - the choice of an *inappropriate block cipher mode* (don't use ECB!)
   - the *misapplication of the algorithm's concepts* (don't reuse IVs or nonces!)
   - the *misuse of an API* (don't reuse ciphers that were initialized with an IV or nonce! - a special case of the previous point)

