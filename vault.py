import os
import json
import base64
import shutil
from encryption import derive_key, encrypt, decrypt

VAULT_DIR = os.path.join(os.path.expanduser("~"), ".pypassvault")
MASTER_FILE = os.path.join(VAULT_DIR, "master.json")
ATTEMPTS_FILE = os.path.join(VAULT_DIR, "attempts.json")

MAX_FAILED_ATTEMPTS = 20


def setup_vault_dir():
    if not os.path.exists(VAULT_DIR):
        os.makedirs(VAULT_DIR)


def is_vault_created():
    return os.path.exists(MASTER_FILE)


def create_vault(master_password):
    setup_vault_dir()
    salt = os.urandom(16)
    key = derive_key(master_password, salt)

    test_data = encrypt("VAULT_OK", key)
    master_info = {
        "salt": base64.b64encode(salt).decode(),
        "verify": test_data,
    }

    with open(MASTER_FILE, "w") as f:
        json.dump(master_info, f)

    return key, salt


def unlock_vault(master_password):
    # check if already locked out before even trying
    failed = get_failed_attempts()
    if failed >= MAX_FAILED_ATTEMPTS:
        print("\n⚠️  BRUTE-FORCE DETECTED! Too many failed attempts.")
        print("💀 SELF-DESTRUCT ACTIVATED — All vault data destroyed.")
        nuke_vault()
        return None, None

    with open(MASTER_FILE, "r") as f:
        master_info = json.load(f)

    salt = base64.b64decode(master_info["salt"])
    key = derive_key(master_password, salt)

    try:
        result = decrypt(master_info["verify"], key)
        if result == "VAULT_OK":
            reset_failed_attempts()
            return key, salt
    except Exception:
        pass

    # wrong password — increment counter
    failed = increment_failed_attempts()
    remaining = MAX_FAILED_ATTEMPTS - failed
    if remaining > 0:
        print(f"⚠️  Wrong password! {remaining} attempt(s) remaining before SELF-DESTRUCT.")
    else:
        print("\n⚠️  BRUTE-FORCE DETECTED! Maximum failed attempts reached.")
        print("💀 SELF-DESTRUCT ACTIVATED — All vault data destroyed.")
        nuke_vault()

    return None, None


def get_failed_attempts():
    """Read the current failed attempt count from disk."""
    if not os.path.exists(ATTEMPTS_FILE):
        return 0
    try:
        with open(ATTEMPTS_FILE, "r") as f:
            data = json.load(f)
        return data.get("failed_attempts", 0)
    except (json.JSONDecodeError, IOError):
        return 0


def increment_failed_attempts():
    """Increment and persist the failed attempt counter. Returns new count."""
    count = get_failed_attempts() + 1
    setup_vault_dir()
    with open(ATTEMPTS_FILE, "w") as f:
        json.dump({"failed_attempts": count}, f)
    return count


def reset_failed_attempts():
    """Reset the failed attempt counter (called on successful login)."""
    if os.path.exists(ATTEMPTS_FILE):
        os.remove(ATTEMPTS_FILE)


def nuke_vault():
    """Destroy ALL vault data — every file in the vault directory. No recovery."""
    if os.path.exists(VAULT_DIR):
        shutil.rmtree(VAULT_DIR)
    print("🔥 All vault data has been permanently destroyed.")
    print("ℹ️  You can start fresh by running PyPassVault again.")


def reset_vault():
    """Manually reset the vault — wipes everything and starts clean."""
    if os.path.exists(VAULT_DIR):
        shutil.rmtree(VAULT_DIR)
    print("🔄 Vault has been completely reset.")
    print("ℹ️  All passwords and settings have been erased.")
    print("ℹ️  Run PyPassVault again to create a new vault.")


def get_vault_file(category):
    return os.path.join(VAULT_DIR, f"{category}.json")


def load_passwords(category, key):
    filepath = get_vault_file(category)
    if not os.path.exists(filepath):
        return {}

    with open(filepath, "r") as f:
        encrypted_entries = json.load(f)

    passwords = {}
    for name, enc_data in encrypted_entries.items():
        passwords[name] = json.loads(decrypt(enc_data, key))

    return passwords


def save_passwords(category, passwords, key):
    setup_vault_dir()
    encrypted_entries = {}
    for name, data in passwords.items():
        encrypted_entries[name] = encrypt(json.dumps(data), key)

    filepath = get_vault_file(category)
    with open(filepath, "w") as f:
        json.dump(encrypted_entries, f, indent=2)


def add_password(category, name, username, password, key):
    passwords = load_passwords(category, key)
    passwords[name] = {
        "username": username,
        "password": password,
    }
    save_passwords(category, passwords, key)


def get_password(category, name, key):
    passwords = load_passwords(category, key)
    return passwords.get(name, None)


def delete_password(category, name, key):
    passwords = load_passwords(category, key)
    if name in passwords:
        del passwords[name]
        save_passwords(category, passwords, key)
        return True
    return False


def list_categories():
    setup_vault_dir()
    categories = []
    for f in os.listdir(VAULT_DIR):
        if f.endswith(".json") and f != "master.json" and f != "attempts.json":
            categories.append(f.replace(".json", ""))
    return categories


def list_entries(category, key):
    passwords = load_passwords(category, key)
    return list(passwords.keys())
