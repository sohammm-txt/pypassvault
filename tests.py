import os
import sys
import shutil

TEST_DIR = os.path.join(os.path.dirname(__file__), '_test_vault_tmp')

import vault
vault.VAULT_DIR = TEST_DIR
vault.MASTER_FILE = os.path.join(TEST_DIR, 'master.json')
vault.ATTEMPTS_FILE = os.path.join(TEST_DIR, 'attempts.json')

from encryption import derive_key, encrypt, decrypt
from vault import (
    create_vault, unlock_vault,
    add_password, get_password, delete_password,
    list_categories, list_entries,
    get_failed_attempts, increment_failed_attempts,
    reset_failed_attempts, nuke_vault, reset_vault,
    is_reserved_category,
)
from utils import generate_password

if os.path.exists(TEST_DIR):
    shutil.rmtree(TEST_DIR)

passed = 0
failed = 0


def check(label, ok):
    global passed, failed
    status = 'PASS' if ok else 'FAIL'
    print(f'  {status}: {label}')
    if ok:
        passed += 1
    else:
        failed += 1


# --- encryption ---
print('Encryption')

salt = os.urandom(16)
key = derive_key('testpass', salt)
check('key length 32', len(key) == 32)

enc = encrypt('hello', key)
check('encrypted not empty', len(enc) > 0)
check('encrypted differs from plain', enc != 'hello')

check('decrypt matches', decrypt(enc, key) == 'hello')

bad_key = derive_key('wrong', salt)
try:
    decrypt(enc, bad_key)
    check('wrong key errors', False)
except Exception:
    check('wrong key errors', True)


# --- vault ---
print('\nVault basics')

key, salt = create_vault('master123')
check('master file exists', os.path.exists(vault.MASTER_FILE))

k2, _ = unlock_vault('master123')
check('correct pw unlocks', k2 is not None)

bad, _ = unlock_vault('nope')
check('wrong pw rejected', bad is None)


# --- passwords ---
print('\nPassword storage')

add_password('social', 'twitter', 'john@x.com', 'abc123', key)
e = get_password('social', 'twitter', key)
check('stored and retrieved', e is not None)
check('username ok', e['username'] == 'john@x.com')
check('password ok', e['password'] == 'abc123')

add_password('social', 'insta', 'john_ig', 'igpass', key)
check('multiple entries', len(list_entries('social', key)) == 2)
check('category shows up', 'social' in list_categories())

delete_password('social', 'twitter', key)
check('deleted', get_password('social', 'twitter', key) is None)
check('other entry remains', len(list_entries('social', key)) == 1)

# delete last entry -> category file should be cleaned up
delete_password('social', 'insta', key)
check('empty category removed', 'social' not in list_categories())


# --- reserved categories ---
print('\nReserved categories')
check('master is reserved', is_reserved_category('master'))
check('attempts is reserved', is_reserved_category('attempts'))
check('social is not reserved', not is_reserved_category('social'))
check('path traversal is reserved', is_reserved_category('../bad'))
check('empty category is reserved', is_reserved_category(''))


# --- password generator ---
print('\nPassword generator')

pwd = generate_password(20)
check('correct length', len(pwd) == 20)
check('two differ', pwd != generate_password(20))
check('min length clamp', len(generate_password(1)) == 4)

has_lower = any(c.islower() for c in pwd)
has_upper = any(c.isupper() for c in pwd)
has_digit = any(c.isdigit() for c in pwd)
check('has mixed chars', has_lower and has_upper and has_digit)


# --- brute force ---
print('\nBrute-force defense')

reset_failed_attempts()
check('starts at 0', get_failed_attempts() == 0)

increment_failed_attempts()
increment_failed_attempts()
check('incremented to 2', get_failed_attempts() == 2)

reset_failed_attempts()
check('reset to 0', get_failed_attempts() == 0)

if os.path.exists(TEST_DIR):
    shutil.rmtree(TEST_DIR)
key, salt = create_vault('master123')
add_password('social', 'tw', 'u@x.com', 'p', key)
check('data before nuke', os.path.exists(vault.MASTER_FILE))

for _ in range(19):
    increment_failed_attempts()
check('19 tracked', get_failed_attempts() == 19)

bad, _ = unlock_vault('totallyWrong')
check('20th returns None', bad is None)
check('vault dir gone', not os.path.exists(TEST_DIR))


# --- reset ---
print('\nVault reset')

key, salt = create_vault('master123')
add_password('work', 'gh', 'dev@x.com', 'ghp', key)
check('exists before reset', os.path.exists(vault.MASTER_FILE))

reset_vault()
check('gone after reset', not os.path.exists(TEST_DIR))


# cleanup
if os.path.exists(TEST_DIR):
    shutil.rmtree(TEST_DIR)

print(f'\n{"=" * 30}')
print(f'  {passed} passed, {failed} failed')
print(f'{"=" * 30}')

if failed:
    sys.exit(1)
