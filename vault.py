import os
import json
import base64
import shutil
from encryption import derive_key, encrypt, decrypt

VAULT_DIR = os.path.join(os.path.expanduser('~'), '.pypassvault')
MASTER_FILE = os.path.join(VAULT_DIR, 'master.json')
ATTEMPTS_FILE = os.path.join(VAULT_DIR, 'attempts.json')

MAX_ATTEMPTS = 20

# categories that would collide with internal filenames
_RESERVED = {'master', 'attempts'}


def _ensure_dir():
    os.makedirs(VAULT_DIR, exist_ok=True)


def is_vault_created():
    return os.path.exists(MASTER_FILE)


def create_vault(master_password):
    _ensure_dir()
    _clear_attempts()
    salt = os.urandom(16)
    key = derive_key(master_password, salt)

    token = encrypt('VAULT_OK', key)
    with open(MASTER_FILE, 'w') as f:
        json.dump({
            'salt': base64.b64encode(salt).decode(),
            'verify': token,
        }, f)

    return key, salt


def unlock_vault(master_password):
    attempts = _get_attempts()
    if attempts >= MAX_ATTEMPTS:
        _self_destruct()
        return None, None

    with open(MASTER_FILE) as f:
        info = json.load(f)

    salt = base64.b64decode(info['salt'])
    key = derive_key(master_password, salt)

    try:
        if decrypt(info['verify'], key) == 'VAULT_OK':
            _clear_attempts()
            return key, salt
    except Exception:
        pass

    attempts = _bump_attempts()
    left = MAX_ATTEMPTS - attempts
    if left > 0:
        print(f'Wrong password. {left} tries left before self-destruct.')
    else:
        _self_destruct()

    return None, None


# --- attempt tracking --------------------------------------------------------

def _get_attempts():
    if not os.path.exists(ATTEMPTS_FILE):
        return 0
    try:
        with open(ATTEMPTS_FILE) as f:
            return json.load(f).get('n', 0)
    except (json.JSONDecodeError, IOError):
        return 0


def _bump_attempts():
    n = _get_attempts() + 1
    _ensure_dir()
    with open(ATTEMPTS_FILE, 'w') as f:
        json.dump({'n': n}, f)
    return n


def _clear_attempts():
    if os.path.exists(ATTEMPTS_FILE):
        os.remove(ATTEMPTS_FILE)


# public aliases so tests can import them
get_failed_attempts = _get_attempts
increment_failed_attempts = _bump_attempts
reset_failed_attempts = _clear_attempts


# --- destructive ops ---------------------------------------------------------

def _self_destruct():
    if os.path.exists(VAULT_DIR):
        shutil.rmtree(VAULT_DIR)
    print('Self-destruct triggered. All vault data wiped.')
    print('Run PyPassVault again to start over.')

nuke_vault = _self_destruct


def reset_vault():
    if os.path.exists(VAULT_DIR):
        shutil.rmtree(VAULT_DIR)
    print('Vault reset. Everything deleted.')
    print('Run PyPassVault again to set up a new vault.')


# --- category / password CRUD ------------------------------------------------

def _cat_file(category):
    return os.path.join(VAULT_DIR, f'{category}.json')


def is_reserved_category(name):
    norm = name.strip().lower()
    return norm in _RESERVED or '/' in norm or '\\' in norm or not norm or norm.startswith('.')


def _load(category, key):
    path = _cat_file(category)
    if not os.path.exists(path):
        return {}
    try:
        with open(path) as f:
            raw = json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

    entries = {}
    for name, data in raw.items():
        try:
            entries[name] = json.loads(decrypt(data, key))
        except Exception:
            print(f"Warning: Failed to decrypt entry '{name}' in category '{category}'.")
    return entries


def _save(category, entries, key):
    _ensure_dir()
    path = _cat_file(category)
    if not entries:
        # don't leave empty category files lying around
        if os.path.exists(path):
            os.remove(path)
        return
    enc = {name: encrypt(json.dumps(data), key) for name, data in entries.items()}
    with open(path, 'w') as f:
        json.dump(enc, f, indent=2)


def add_password(category, name, username, password, key):
    entries = _load(category, key)
    entries[name] = {'username': username, 'password': password}
    _save(category, entries, key)


def get_password(category, name, key):
    return _load(category, key).get(name)


def delete_password(category, name, key):
    entries = _load(category, key)
    if name not in entries:
        return False
    del entries[name]
    _save(category, entries, key)
    return True


def list_categories():
    _ensure_dir()
    out = []
    for fname in os.listdir(VAULT_DIR):
        if fname.endswith('.json') and fname not in ('master.json', 'attempts.json'):
            out.append(fname[:-5])
    return out


def list_entries(category, key):
    return list(_load(category, key).keys())
