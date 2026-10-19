# PyPassVault

A lightweight CLI password manager for Linux, macOS, and Windows. Stores credentials in encrypted JSON files on your local machine using AES-256-GCM.

---

## Features

- **AES-256-GCM encryption** with authenticated tags to prevent tampering.
- **PBKDF2 key derivation** using HMAC-SHA256 with 100,000 iterations and a random 16-byte salt.
- **Per-entry nonces** — a fresh 12-byte random nonce is generated for every encryption call.
- **Categorized vaults** — split credentials by category (e.g., `work`, `personal`, `finance`), each saved to its own file.
- **Built-in password generator** using Python's `secrets` module, guaranteeing a blend of uppercase, lowercase, numbers, and symbols.
- **Failed attempt limiter** — automatically deletes all vault files after 20 consecutive incorrect master password attempts to limit guessing through the app.
- **Vault reset option** — built-in option to wipe the local vault directory and start fresh.

---

## Requirements

- Python 3.8+
- `cryptography`

---

## Installation

```bash
git clone https://github.com/sohammm-txt/pypassvault.git
cd pypassvault
pip install -r requirements.txt
```

---

## Usage

Start the application:

```bash
python3 main.py
```

### Initial Setup

When running for the first time, you will be prompted to create your master password:

```
========================================
   PyPassVault - Password Manager
========================================

No vault found. Creating one now.
Master password: 
Confirm: 
Vault created.
```

### Main Menu

On subsequent launches, enter your master password to unlock:

```
========================================
   PyPassVault - Password Manager
========================================
Master password: 
Unlocked.

--- Menu ---
1. Add password
2. View password
3. List entries
4. Delete password
5. Generate password
6. Reset vault
7. Quit

> 
```

### Adding an Entry

```
> 1
Category (e.g. social, work): email
Entry name: proton
Username/email: user@pm.me
Generate random password? (y/n): y
Length (default 16): 20
Generated: nK#9vX!pT2&mLw$jQ5@r
Saved 'proton' in 'email'.
```

### Viewing an Entry

```
> 2
Categories: email, work
Category: email
Entries: proton
Entry: proton
  User: user@pm.me
  Pass: nK#9vX!pT2&mLw$jQ5@r
```

### Listing Entries

```
> 3

[email]
  - proton

[work]
  - github
  - slack
```

---

## Storage Layout

All data is stored in the user's home folder under `~/.pypassvault/`:

- `master.json`: Contains the base64-encoded salt and an encrypted validation token (`VAULT_OK`) used to verify your master password. The master password itself is never written to disk.
- `attempts.json`: Persists the count of consecutive failed unlock attempts. Cleared on successful unlock.
- `<category>.json`: Contains dictionary mappings of entry names to base64-encoded ciphertext blocks (nonce prepended to ciphertext + auth tag). Empty category files are deleted automatically when their last entry is removed.

---

## Security Model

1. **Key Derivation**: Keys are derived from the master password and a 16-byte random salt using PBKDF2-HMAC-SHA256 with 100,000 iterations, yielding a 256-bit key.
2. **Authenticated Encryption**: Entries are encrypted using AES-256 in Galois/Counter Mode (GCM). An error is raised and decryption fails if the ciphertext or authentication tag is modified.
3. **Random Nonces**: Each encryption operation uses `os.urandom(12)` to generate an IV/nonce, ensuring identical credentials encrypt to different ciphertexts.
4. **Brute-Force Mitigation**: A local counter increments on every failed login attempt. After 20 consecutive failures, the vault directory is wiped to limit guessing through the app.

---

## Running Tests

Run the test suite with:

```bash
python3 tests.py
```

Expected output:

```
Encryption
  PASS: key length 32
  PASS: encrypted not empty
  PASS: encrypted differs from plain
  PASS: decrypt matches
  PASS: wrong key errors

Vault basics
  PASS: master file exists
  PASS: correct pw unlocks
Wrong password. 19 tries left before self-destruct.
  PASS: wrong pw rejected

Password storage
  PASS: stored and retrieved
  PASS: username ok
  PASS: password ok
  PASS: multiple entries
  PASS: category shows up
  PASS: deleted
  PASS: other entry remains
  PASS: empty category removed

Reserved categories
  PASS: master is reserved
  PASS: attempts is reserved
  PASS: social is not reserved
  PASS: path traversal is reserved
  PASS: empty category is reserved

Password generator
  PASS: correct length
  PASS: two differ
  PASS: min length clamp
  PASS: has mixed chars

Brute-force defense
  PASS: starts at 0
  PASS: incremented to 2
  PASS: reset to 0
  PASS: data before nuke
  PASS: 19 tracked
Self-destruct triggered. All vault data wiped.
Run PyPassVault again to start over.
  PASS: 20th returns None
  PASS: vault dir gone

Vault reset
  PASS: exists before reset
Vault reset. Everything deleted.
Run PyPassVault again to set up a new vault.
  PASS: gone after reset

==============================
  34 passed, 0 failed
==============================
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.