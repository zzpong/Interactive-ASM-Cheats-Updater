"""Select user keys consistently, without logging or embedding key values."""
from pathlib import Path
import re


def select_key_file(root, home=None):
    root = Path(root)
    home = Path.home() if home is None else Path(home)
    candidates = (root / 'prod.keys', home / '.switch' / 'prod.keys', root / 'keys.txt')
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError('Keys not found: use prod.keys in the app directory or ~/.switch/')


def read_keys(path):
    keys = {}
    with open(path, encoding='utf-8-sig') as stream:
        for number, line in enumerate(stream, 1):
            line = line.split('#', 1)[0].strip()
            if not line or '=' not in line:
                continue
            name, value = (part.strip() for part in line.split('=', 1))
            name = name.lower()
            if not re.fullmatch(r'[a-z0-9_]+', name):
                raise ValueError('Invalid key name at line %d' % number)
            if not re.fullmatch(r'(?:[a-fA-F0-9]{2})+', value):
                raise ValueError('Invalid key encoding for %s at line %d' % (name, number))
            decoded = bytes.fromhex(value)
            if name in keys and keys[name] != decoded:
                raise ValueError('Conflicting duplicate key: %s' % name)
            keys[name] = decoded
    return keys
