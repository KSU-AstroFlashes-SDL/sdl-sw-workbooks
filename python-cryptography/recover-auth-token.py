from base64 import b64decode
from os import getenv
import string
import subprocess
import sys
from types import FunctionType

from aescrypt import encrypt

ALPHABET = string.ascii_letters + string.digits

if (debug := getenv("DEBUG")) and debug in "1Yy":
    def _DEBUG(*msgs, **extra):
        for msg in msgs:
            print(f"{msg}", file=sys.stderr)
        for (name, value) in extra.items():
            print(f"\u21b3 {name}: {value}", file=sys.stderr)
    _DEBUG.enabled = True
else:
    def _DEBUG(*msgs, **extra):
        pass
    _DEBUG.enabled = False

# Note: You will not find a reference to the secret key in this script.
# Nor are we required to be in possession of any "intercepted" ciphertext.
# The use of ECB mode, combined with the format/structure of the plaintext (and
# the fact that we have access to an encryption oracle) means that we'll be
# able to recover the "secret" authentication token using ONLY the oracle!

# An oracle is some service available to the adversary. It could be as simple
# as the "make-admin.py" script we use here; it could be a Web service; it
# could even be a Web page/portal if the adversary has read access to an
# associated database!
# Most often the adversary will define an oracle *function* (to automate the
# invocation of the oracle).
# (Even in cases where access to the actual oracle is rate-limited, the
# adversary can EASILY determine that limit and implement this function
# appropriately - the ONLY downside being the overall time to recovery!)
def encryption_oracle(plaintext: bytes) -> bytes:
    args = ["python", "make-admin.py", plaintext.decode("ascii")]
    completed = subprocess.run(args, capture_output=True, text=True,
                               check=True)
    _DEBUG(f"{args!r}", output=completed.stdout.strip())
    return b64decode(completed.stdout)


# this just allows us to more easily visualize ciphertext blocks
def _debug_hex_blocks(label: str, ct: bytes, blksz: int, indent: str=' '):
    _DEBUG(f"{label}:")
    if _DEBUG.enabled:
        for b in range(0, len(ct) // blksz):
            block = f"{indent}{b:2d}:"
            i = b * blksz
            j = i + blksz
            for x in ct[i:j]:
                block += f" {x:02x}"
            _DEBUG(f"{block}")


# This isn't even necessary if we know the algorithm (e.g. AES always has a
# block size of 16 bytes), but is implemented here to demonstrate how trivial
# it is! (recall Kerckhoffs's principle!)
def discern_block_size(oracle: FunctionType):
    min_valid_account = b'Z'
    min_valid_email = min_valid_account + b"@example.com"
    min_ctlen = len(oracle(min_valid_email))
    _DEBUG("discern_block_size", email=min_valid_email, ctlen=min_ctlen)

    # a range that's open for double the largest practical block size gives us
    # more than reasonable flexibility while avoiding the possibility of an
    # infinite loop
    for i in range(1, 64):
        email_i = (i * b'Z') + min_valid_email
        ctlen_i = len(oracle(email_i))
        _DEBUG("discern_block_size", email=email_i, ctlen=ctlen_i)
        if ctlen_i > min_ctlen:
            return ctlen_i - min_ctlen

    raise RuntimeError("oracle did not reveal block size!")


if __name__ == "__main__":
    # Q: What does an adversary KNOW?
    # A: Whatever the make-admin.py script (i.e. the "oracle") and/or the
    #    documentation divulges!
    #
    # For example:
    #
    # $ python make-admin.py -h
    # USAGE: python make-admin.py <account>@example.com
    # Generate the Vendor, Inc. admin login credential for <account>:
	# base64(encrypt("<account><vendor-admin-auth-token>"))
    #
    # Now we know:
    #       (a) the prefix "<account>"
    #           Note that WE (the adversary) control <account>!
    #       (b) the ciphertext output
    #           Since we know that ECB mode is used, we know that we can
    #           "influence" the output
    #           (b/c ECB means same-input -> same-output!)
    #       (c) that only a subset of ASCII input is accepted (this from the
    #           "documentation" of the Vendor, Inc. algorithm - see
    #           make-admin.py)
    #           This REDUCES our potential "alphabet" to digits & upper/lower
    #           case ASCII letters
    #           (This is significant - there are 256 possible byte values,
    #           but reducing those possibilities to 62 (10 + 2*26) means
    #           we have almost 200 *less* possibilities that we need to account
    #           for when we are recovering the authentication code!)

    # What can an adversary DISCOVER?
    # (We don't NEED this in most cases b/c we'll already know which encryption
    # algorithm is in use - e.g. AES will ALWAYS be block size 16! We include
    # it here to demonstrate how trivial it is to discover.)
    blksz = discern_block_size(encryption_oracle)
    _DEBUG(f"block size = {blksz}")

    # Since we KNOW...:
    # (a) block size is 16
    # (b) plaintext structure is "<account><vendor-admin-auth-token>"
    #
    # ...then we ALSO know that we can "force" a 16-byte input block to the
    # encryptor (e.g. by using 'ZZZZZZZZZZZZZZZZ' -- 16 Z's -- for <account>)
    # Why does this matter? Two reasons:
    # (1) allows us to discover the maximum length for the authentication token
    # (which in turn)
    # (2) allows us to figure out how many *additional* ('Z' * 16) blocks of
    #     input we need in order to recover the full authentication token

    # First let's figure out the min/max length of the authentication token
    # that we're trying to steal.

    # We already know the min length implicitly; we know that the
    # authentication token must EXIST (so it has to be at least one byte)
    min_auth_token_len = 1

    # To figure out the max length, we first need to know how many bytes of
    # ciphertext are produced by our minimum valid input (i.e. an account name
    # of length one):
    ctlen = len(encryption_oracle(b"Z@example.com"))

    # The ctlen will be a multiple of blksz, so we can now start to "count
    # backward" to determine the maximum authentication token length.
    # We know the plaintext was "<account><vendor-admin-auth-token>", so begin
    # by deducting len(<account>) (i.e. 1), then account for the fact that
    # there will be at least 1 byte of PKCS#7 padding (otherwise our ctlen
    # would extend ANOTHER blksz number of bytes!)
    # (Note also that ctlen here will ALWAYS be > min_auth_token_len due to
    # PKCS#7 padding and the AES block size)
    max_auth_token_len = ctlen - 1 - 1

    # To recover the FULL authentication token, we'll need an amount of "fake"
    # padding bytes that is the minimum MULTIPLE of blksz that is > the
    # max_auth_token_len we just found above.
    # (Using our oracle, this means an "account" length of N*blksz.)
    # Fortunately, this is just ctlen ;)
    # Why?
    # If we use an account length that is EQUAL to ctlen, then we have exactly
    # the right amount of "buffer" to accommodate all recovered bytes of the
    # authentication token!
    acct_len = ctlen
    controlled_input = ('Z' * acct_len) + "@example.com"
    controlled_ct = encryption_oracle(controlled_input.encode("ascii"))
    _DEBUG(f"blocks < {acct_len//blksz} are the \"controlled input\"",
            f"blocks >= {acct_len//blksz} are the encrypted authentication token")
    _debug_hex_blocks(f"controlled_input {controlled_input!r}",
                      controlled_ct, blksz)
    alt_input = ('A' * acct_len) + "@example.com"
    alt_ct = encryption_oracle(alt_input.encode("ascii"))
    _DEBUG("Notice how ECB produces same encrypted authentication token "
           "block(s) even if we change our controlled input (as long as we "
           "maintain the same block boundary)")
    _debug_hex_blocks(f"alt_input {alt_input!r}", alt_ct, blksz)

    # Most importantly, this means that the authorization token (which is the
    # secret we're trying to recover) begins at the FIRST BYTE of the NEXT
    # encryption block AFTER the account (which we control).
    #
    # Since we already know that ECB produces same ciphertext output for same
    # plaintext input, what if we *shortened* our input block (account) by a
    # single byte? i.e. ('Z' * (acct_len - 1)) + "@example.com"
    # Now the LAST byte of ciphertext output will correspond to the FIRST byte
    # of the authentication token!
    #
    # This lets us take advantage of the information provided by the oracle,
    # and only check our actual ciphertext block against the ALPHABET guesses.
    #
    # We'll also need to keep track of what we've recovered so far, so that we
    # can continue deducting one of our fake pad bytes in favor of appending
    # the next-discovered token byte.
    recovered = ""
    for i in range(1, acct_len):
        # always i bytes "short" of a block boundary; this means that i bytes
        # of the secret get encrypted at the END of the block boundary
        short_acct = 'Z' * (acct_len - i)
        short_input = short_acct + "@example.com"
        next_ct = encryption_oracle(short_input.encode("ascii"))
        _debug_hex_blocks(f"short_input {short_input!r}?", next_ct, blksz)
        _DEBUG(f"Trying to match {next_ct[:blksz].hex()}...")
        matched = False
        for guess in ALPHABET:
            # always an EXACT multiple of blksz; however short_acct & recovered
            # are KNOWN (i.e. controlled), so we successfully "guess" the next
            # byte of the secret when we get a matching block!
            guess_acct = short_acct + recovered + guess
            guess_input = guess_acct + "@example.com"
            guess_ct = encryption_oracle(guess_input.encode("ascii"))
            _debug_hex_blocks(f"guess {guess!r} guess_input {guess_input!r}",
                              guess_ct, blksz)
            if guess_ct[:blksz] == next_ct[:blksz]:
                # guess is correct; we've recovered the next byte!
                recovered += guess
                matched = True
                print(f"RECOVERED: {recovered!r}")
                break   # inner (guess) loop
        if not matched:
            break   # outer (i) loop

    sys.exit(0
             if len(recovered) >= min_auth_token_len and
                len(recovered) <= max_auth_token_len
             else 1)

# P.S. - This recovery script has a defect! This script *works*, and
# demonstrably proves the weakness of ECB mode, but the defect is that there is
# a LIMITATION to this script's effectiveness.
#
# CHALLENGE #1: Can you discover the limitation defect?
#
# CHALLENGE #2: Can you find (or reason about) a fix to the limitation defect?
# (Hint: What if Vendor decided to use an authentication token with entropy
# >=100 but WITHOUT changing the ALPHABET? You MAY need to solve the
# make-admin.py challenge before you can solve this one!)

