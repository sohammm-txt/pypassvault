import os
import sys
import shutil
import base64

# use a temp vault dir so tests don't mess with real data
TEST_VAULT_DIR = os.path.join(os.path.dirname(__file__), "_test_vault_tmp")

# patch vault.py to use our test directory
import vault
vault.VAULT_DIR = TEST_VAULT_DIR
vault.MASTER_FILE = os.path.join(TEST_VAULT_DIR, "master.json")
vault.ATTEMPTS_FILE = os.path.join(TEST_VAULT_DIR, "attempts.json")

from encryption import derive_key, encrypt, decrypt
from vault import (
    create_vault, unlock_vault,
    add_password, get_password, delete_password,
    list_categories, list_entries,
    get_failed_attempts, increment_failed_attempts,
    reset_failed_attempts, nuke_vault, reset_vault,
)
from utils import generate_password

# cleanup before starting
if os.path.exists(TEST_VAULT_DIR):
    shutil.rmtree(TEST_VAULT_DIR)

passed = 0
failed = 0


def test(name, condition):
    global passed, failed
    if condition:
        print(f"  PASS: {name}")
        passed += 1
    else:
        print(f"  FAIL: {name}")
        failed += 1


# --- encryption tests ---
print("Testing encryption...")

salt = os.urandom(16)
key = derive_key("testpassword123", salt)
test("Key is 32 bytes (256 bits)", len(key) == 32)

encrypted = encrypt("hello world", key)
test("Encrypted data is not empty", len(encrypted) > 0)
test("Encrypted != original", encrypted != "hello world")

decrypted = decrypt(encrypted, key)
test("Decrypted matches original", decrypted == "hello world")

wrong_key = derive_key("wrongpassword", salt)
try:
    decrypt(encrypted, wrong_key)
    test("Wrong key raises error", False)
except Exception:
    test("Wrong key raises error", True)


# --- vault tests ---
print("\nTesting vault...")

key, salt = create_vault("master123")
test("Vault file created", os.path.exists(vault.MASTER_FILE))

key2, salt2 = unlock_vault("master123")
test("Correct password unlocks vault", key2 is not None)

bad_key, _ = unlock_vault("wrongpassword")
test("Wrong password rejected", bad_key is None)


# --- password storage tests ---
print("\nTesting password storage...")

add_password("social", "twitter", "john@email.com", "mypass123", key)
entry = get_password("social", "twitter", key)
test("Password stored and retrieved", entry is not None)
test("Username matches", entry["username"] == "john@email.com")
test("Password matches", entry["password"] == "mypass123")

add_password("social", "instagram", "john_insta", "instapass", key)
entries = list_entries("social", key)
test("Multiple entries stored", len(entries) == 2)

categories = list_categories()
test("Category listed", "social" in categories)

delete_password("social", "twitter", key)
entry = get_password("social", "twitter", key)
test("Password deleted", entry is None)

remaining = list_entries("social", key)
test("Other entries still exist", len(remaining) == 1)


# --- password generator tests ---
print("\nTesting password generator...")

pwd = generate_password(20)
test("Generated password correct length", len(pwd) == 20)

pwd2 = generate_password(20)
test("Two passwords are different", pwd != pwd2)

short = generate_password(8)
test("Short password works", len(short) == 8)


# --- brute-force defense tests ---
print("\nTesting brute-force defense...")

# clear any leftover state from previous tests
reset_failed_attempts()

# fresh state — no failed attempts
test("Initial failed attempts is 0", get_failed_attempts() == 0)

# increment attempts
increment_failed_attempts()
increment_failed_attempts()
test("Failed attempts incremented to 2", get_failed_attempts() == 2)

# reset on successful login
reset_failed_attempts()
test("Failed attempts reset to 0", get_failed_attempts() == 0)

# simulate reaching max attempts — recreate vault first
if os.path.exists(TEST_VAULT_DIR):
    shutil.rmtree(TEST_VAULT_DIR)
key, salt = create_vault("master123")
add_password("social", "twitter", "john@email.com", "mypass123", key)

# verify data exists before nuke
test("Data exists before nuke", os.path.exists(vault.MASTER_FILE))

# simulate 19 wrong attempts
for i in range(19):
    increment_failed_attempts()
test("19 failed attempts tracked", get_failed_attempts() == 19)

# 20th attempt — triggers self-destruct
bad_key, _ = unlock_vault("totallyWrongPassword!!")
test("20th wrong attempt returns None", bad_key is None)
test("Vault directory destroyed after self-destruct", not os.path.exists(TEST_VAULT_DIR))


# --- vault reset tests ---
print("\nTesting vault reset...")

# recreate vault, add data, then reset
key, salt = create_vault("master123")
add_password("work", "github", "dev@email.com", "ghpass", key)
test("Vault exists before reset", os.path.exists(vault.MASTER_FILE))

reset_vault()
test("Vault directory gone after reset", not os.path.exists(TEST_VAULT_DIR))


# cleanup
if os.path.exists(TEST_VAULT_DIR):
    shutil.rmtree(TEST_VAULT_DIR)

print(f"\n{'=' * 35}")
print(f"  Results: {passed} passed, {failed} failed")
print(f"{'=' * 35}")

if failed > 0:
    sys.exit(1)
