"""Generate a Vendor, Inc. admin authentication credential."""

import sys
from base64 import b64encode


def validated_account(email: str) -> str:
    if not email:
        raise ValueError("email address is required")

    try:
        local, domain = email.split("@")
    except:
        raise ValueError(f"{email!r} is not a valid email address")

    # not pedantic; matches organizational policy
    if local == "":
        raise ValueError(f"{email!r} is not a valid email address")
    elif domain != "example.com":
        raise ValueError("only '@example.com' users may be granted admin access")

    return local


def get_vendor_admin_auth_token() -> str:
    # This is what an adversary wants to recover.
    # (demo only; in reality this is produced by a (presumably) secure,
    # reliable algorithm/service; though its "alphabet" is typically known)
    return "uPa2ADIX7vx"

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
    from argparse import ArgumentParser

    parser = ArgumentParser(
        usage=__doc__,
        epilog='Admin authentication credentials are in the format base64(encrypt("<account><vendor-admin-auth-token>"))',
    )
    parser.add_argument(
        "email", help="the admin user's email address (i.e. <account>@example.com)"
    )
    parser.add_argument(
        "--cbc",
        action="store_true",
        help="use AES in CBC mode (default is AES in ECB mode)",
    )

    args = parser.parse_args()

    if args.cbc:
        from cbccrypt import decrypt, encrypt
    else:  # ECB mode
        from ecbcrypt import decrypt, encrypt

    account = validated_account(args.email)
    authorization = f"{account}{get_vendor_admin_auth_token()}"

    pt = authorization.encode("utf-8")
    ct = encrypt(pt)

    # sanity check
    assert decrypt(ct) == pt

    print(b64encode(ct).decode("ascii"))

    sys.exit(0)
