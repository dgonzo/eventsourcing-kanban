import re
from email.utils import parseaddr
from urllib.parse import urlparse

from utility.fixtures import BLACKLIST_DOMAINS

ORG_MATCH = re.compile(r".*@(?P<organization>.*)")


def whitelist_domain(default_domain):
    """Parses a non-blacklisted domain from an email address.

    :param default_domain: Valid domain.
    :raises AttributeError: If email is an invalid email address.
    :returns: A domain.
    """
    if default_domain not in BLACKLIST_DOMAINS:
        return default_domain
    else:
        return "public.example.com"


def valid_email(email):
    parsed = parseaddr(email)
    if '@' and '.' in parsed[1]:
        return True
    else:
        return False


def valid_domain(domain):
    parse = urlparse(domain)
    valid = "." in parse.path
    invalid = "@" in parse.path
    if valid and not invalid:
        return True
    else:
        return False


def valid_encrypted_password(password):
    length = len(password) == 131
    password_match = '$pbkdf2-sha512$200000$' in password
    if length and password_match:
        return True
    else:
        return False


def valid_unencrypted_password(password):
    # import pdb
    # pdb.set_trace()
    password_match = re.compile(
        r"(?=.*?(?P<digit>\d))(?=.*?(?P<caps>[A-Z]))(?=.*?(?P<not_alphanumeric>[!@#$%^&*<>?]))")
    length = len(password) >= 8
    matches = password_match.match(password)
    if length and matches:
        return True
    else:
        return False
