from base64 import b64encode
import sys

from ecbcrypt import encrypt, decrypt


def validated_account(email: str) -> str:
    if not email:
        raise ValueError("email address is required")

    try:
        local, domain = email.split('@')
    except:
        raise ValueError(f"{email!r} is not a valid email address")

    # not pedantic; matches organizational policy
    if local == "":
        raise ValueError(f"{email!r} is not a valid email address")
    elif domain != "example.com":
        raise ValueError(
                "only '@example.com' users may be granted admin access")

    return local


def get_vendor_admin_auth_token() -> str:
    # This is what an adversary wants to recover.
    # (demo only; in reality this is produced by a (presumably) secure,
    # reliable algorithm/service; though its "alphabet" is typically known)
    return "G7kHZ5Xz2SN"

    # This particular token is length 11, randomly generated from the set of
    # all ASCII letters (upper & lower case) and the digits 0-9.
    #
    # CHALLENGE:
    # WHY did the vendor choose a length of 11, *specifically*?
    # (Hint: run a search for "password entropy." Even though this isn't a
    # password per se, the entropy concept still applies.)


_USAGE = (
        f"USAGE: python {sys.argv[0]} <account>@example.com\n"
        "Generate the Vendor, Inc. admin login credential for <account>:\n"
        '\tbase64(encrypt("<account><vendor-admin-auth-token>"))'
        )
if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] in ["-h", "--help", "-?", "/?"]:
        print(_USAGE, file=sys.stderr)
        sys.exit(1)

    account = validated_account(sys.argv[1])
    authorization = f"{account}{get_vendor_admin_auth_token()}"

    pt = authorization.encode("utf-8")
    ct = encrypt(pt)

    # sanity check
    assert decrypt(ct) == pt

    print(b64encode(ct).decode('ascii'))

    sys.exit(0)

