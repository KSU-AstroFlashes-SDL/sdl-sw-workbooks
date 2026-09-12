# Real world: Recover an AES-CBC-encrypted secret due to IV misuse

In Exercise 2 of [Python cryptography](README.md) we learned that CBC "reduces" to ECB when an IV is
re-used.

We've already seen the proof of ECB's weakness via the `make-admin.py` and `recover-auth-token.py`
scripts, so at this point the same weakness of CBC-with-reused-IV should be academically obvious.

But there's no greater "wow" factor than *seeing* an AES-256-encrypted value being revealed right in
front of your eyes, within seconds. So we're going to quickly repeat the same experiment, this time
using an **incorrectly** implemented AES-CBC scheme (in `cbccrypt.py`). As with the previous ECB
experiment, source code comments in `cbccrypt.py` explain more about the problem (and also pose a
challenge to interested developers).

> [!NOTE]
> Before proceeding, there is an important clarification to make.
>
> If you've heard about "AES" before, you've no doubt read about claims that it has no known
> weaknesses, or that it would take longer than the age of the universe to "break" it, or that
> "breaking it" is computationally impossible with any known or theoretically feasible technology
> (future quantum breakthroughs notwithstanding). Each of these statements is true.
>
> How is it possible, then, that we are able to prove demonstrably that we CAN "break" it by
> recovering AES-encrypted values!? The answer lies in a subtle but critical distinction:
>
> We are **NOT** breaking AES - rather, we are breaking a *system* that *misuses* AES. The
> mathematical strength/correctness of the AES *algorithm* remains uncompromised in our
> demonstrations.

> [!TIP]
> Understanding the distinction in the previous note leads to perhaps the single most critical
> "lesson" to learn about cybersecurity (whether at the hardware, network, or middleware/software
> layer):
>
> **The security of any system is only as strong as its WEAKEST link.**
>
> In our demonstrations, the weakest link is misuse/misconfiguration in software. We are able to
> exploit that weakness to compromise the *system*, even though the strength of the AES *algorithm*
> remains intact.

## Confirm that AES is being used incorrectly
As in the ECB demonstration, the [make-admin.py](make-admin.py) script is what allows us to identify
the misuse **and** take advantage of the misuse.

This time, we will ask the script to use our (intentionally) incorrectly-implemented `cbccrypt.py`
library: (notice the additional `--cbc` argument)
```console
python make-admin.py --cbc account@example.com
```
Note the output.
**IF** AES is being used correctly, then executing the same command again should produce *different*
output: (of course, we already know what's going to happen...)
```shell
python make-admin.py --cbc account@example.com
```
As expected, the output is identical. This confirms **incorrect usage** of AES-CBC in
`cbcccrypt.py`.

Take a minute to read through the source code and comments in [cbccrypt.py](cbccrypt.py).

## Recover the secret

Now run the recovery script, being sure to include the `--cbc` argument so that it uses the
"make-admin.py --cbc" encryption oracle:
```shell
python recover-auth-token.py --cbc
```

Sit back and enjoy the show... you'll observe (in real-time) as we recover the secret Vendor admin
authentication code byte-by-byte.

(If you have any doubt as to the effectiveness of the recovery script, go ahead and CHANGE the
authentication token within the `make-admin.py` script. The `recover-auth-token.py` script will
still expose it successfully.)
