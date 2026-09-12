# Real world: Recover an AES-ECB-encrypted secret

In Exercise 1 of [Python cryptography](README.md) we learned that "ECB mode is bad" because *same-plaintext-input* produces *same-ciphertext-output*.  (In simpler terms: ECB mode exposes relationships between plaintext and ciphertext.)

Here, to reinforce (and prove) that weakness, we will observe firsthand that an AES-ECB-encrypted secret can be easily recovered.

> [!NOTE]
> Strictly speaking, it is not **required** to understand *why* or *how* ECB mode is weak; we only need to understand that it is not to be used. (And, of course, to not use it.)
> However, understanding the underlying details *is* valuable, so this supplementary material is provided for those who have an interest in a "deeper dive."
> 
> This article will only show the step-by-step execution of the related scripts.
> 
> Additional information is presented in the comments within those scripts, and is recommended reading for those who wish to understand the concepts.

## Confirm that AES is being used incorrectly
The [make-admin.py](make-admin.py) script is what allows us to identify the misuse **and** take advantage of the misuse. (It's what's called an "encryption oracle," which is explained in more detail in its comments.)
```console
python make-admin.py account@example.com
```
Note the output.
**IF** AES is being used correctly (hint: it is not), then executing the same command again should produce *different* output:
```shell
python make-admin.py account@example.com
```
Notice that the output is identical. This constitutes **incorrect usage** of AES (or of *any* block cipher, for that matter).

## Convince yourself that "the hack is real"
View the [recover-auth-token.py](recover-auth-token.py) script.  You won't find any reference to the secret key, or to the secret authentication token that we're trying to "steal."

The **only** thing we need is the oracle (i.e. the [make-admin.py](make-admin.py) script). (Take a close look at the `encryption_oracle` function in `recover-auth-token.py`.)

## Recover the secret

This is the simplest step: just run the recovery script!
```shell
python recover-auth-token.py
```

Sit back and enjoy the show... you'll observe (in real-time) as we recover the secret Vendor admin authentication code byte-by-byte.

(If you have any doubt as to the effectiveness of the recovery script, go ahead and CHANGE the authentication token within the `make-admin.py` script. The `recover-auth-token.py` script will still expose it successfully.)
