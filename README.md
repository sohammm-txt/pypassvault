# 🔐 PyPassVault

A simple, secure password manager that stores your passwords encrypted with **AES-256** encryption. Built with Python — no fancy frameworks, just clean code that works.

---

## What It Does

PyPassVault is a command-line password manager that:

- Stores all your passwords **locally** on your machine
- Encrypts everything with **AES-256-GCM** (military-grade encryption)
- Organizes passwords into **categories** (social, work, email, etc.)
- Each category gets its own encrypted file
- Generates strong random passwords for you
- **Brute-force defense** — self-destructs after 20 wrong password attempts
- **Vault reset** — wipe everything and start fresh from the menu
- Works on **Windows, macOS, and Linux**

---

## How It Works

### The Encryption Flow

```
Master Password
      │
      ▼
  PBKDF2 (100,000 rounds + random salt)
      │
      ▼
  256-bit AES Key
      │
      ▼
  AES-256-GCM encrypts/decrypts your passwords
```

1. **You set a master password** — this is the only password you need to remember
2. **PBKDF2** takes your master password and a random salt, runs it through 100,000 rounds of SHA-256 hashing to produce a 256-bit encryption key
3. **AES-256-GCM** uses that key to encrypt each password entry with a unique random nonce (so even identical passwords produce different encrypted outputs)
4. Everything is stored as JSON files in `~/.pypassvault/`

### Why AES-256-GCM?

- **AES-256** = 256-bit key = practically unbreakable
- **GCM mode** = provides both encryption AND authentication (detects tampering)
- Each encryption uses a fresh **12-byte random nonce** so the same data encrypts differently every time

---

## Project Structure

```
pypassvault/
├── main.py           # CLI menu — the app entry point
├── encryption.py     # AES-256 encrypt/decrypt functions
├── vault.py          # Password storage (add, get, delete, list)
├── utils.py          # Password generator + input helpers
├── tests.py          # Simple test script (just run it)
├── requirements.txt  # Just one dependency: cryptography
└── README.md         # You're reading this
```

### What Each File Does

| File | Purpose |
|------|---------|
| `encryption.py` | Key derivation (PBKDF2) and AES-256-GCM encrypt/decrypt |
| `vault.py` | All the vault operations — create, unlock, CRUD passwords |
| `utils.py` | Random password generator and input helper functions |
| `main.py` | Interactive menu that ties everything together |
| `tests.py` | Quick tests to make sure everything works |

---

## Setup

### Requirements

- Python 3.7+
- `cryptography` library

### Install

```bash
git clone https://github.com/yourusername/pypassvault.git
cd pypassvault
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

### Run Tests

```bash
python tests.py
```

---

## Usage

### First Run — Create Your Vault

```
========================================
   PyPassVault - Password Manager
   AES-256 Encrypted Storage
========================================

First time? Let's create your vault!
Set your master password: ****
Confirm master password: ****
Vault created successfully!
```

### Adding a Password

```
--- Main Menu ---
1. Add a password
2. View a password
3. List all entries
4. Delete a password
5. Generate a password
6. Reset vault (⚠️  destroys all data)
7. Exit

Your choice: 1
Category (e.g. social, work, email): social
Entry name: twitter
Username/Email: john@email.com
Generate a random password? (y/n): y
Password length (default 16): 20
Generated: kQ#9xM!pR2&nLw$jT5@v
Saved 'twitter' under 'social'!
```

### Viewing a Password

```
Your choice: 2
Categories: social, work
Category: social
Entries: twitter, instagram
Entry name: twitter

  Username: john@email.com
  Password: kQ#9xM!pR2&nLw$jT5@v
```

### Listing Everything

```
Your choice: 3

[social]
  - twitter
  - instagram

[work]
  - slack
  - github
```

### Generating a Password (Without Saving)

```
Your choice: 5
Password length (default 16): 24
Generated: Xn#8kL!mP3$qRw@jT5&vB2*z
```

---

## Where Are My Passwords Stored?

All vault data lives in your home directory:

| OS | Path |
|----|------|
| Linux | `~/.pypassvault/` |
| macOS | `~/.pypassvault/` |
| Windows | `C:\Users\YourName\.pypassvault\` |

Files inside:
- `master.json` — salt + encrypted verification token (NOT your master password)
- `attempts.json` — brute-force attempt counter (auto-managed)
- `social.json` — encrypted passwords in the "social" category
- `work.json` — encrypted passwords in the "work" category
- etc.

> **Note:** Your master password is NEVER stored anywhere. If you forget it, your passwords are gone forever. That's the point of real encryption.

---

## 🛡️ Brute-Force Defense (Self-Destruct)

PyPassVault has a built-in brute-force protection system that **permanently destroys all vault data** after too many wrong password attempts.

### How It Works

```
Wrong password entered
        │
        ▼
  Counter incremented (persisted to disk)
        │
        ▼
  Counter reaches 20?
   ├── NO  → "X attempt(s) remaining" warning
   └── YES → 💀 SELF-DESTRUCT: entire vault directory wiped
```

- **20 consecutive wrong passwords** = all data destroyed permanently
- The counter **persists across sessions** — closing and reopening the app doesn't reset it
- A **successful login** resets the counter back to 0
- After self-destruct, you can start fresh by running PyPassVault again

### What Gets Destroyed

When self-destruct triggers, the **entire** `~/.pypassvault/` directory is deleted:
- All encrypted password files
- The master key file
- The attempt counter itself
- Everything. Gone. No recovery.

### Why This Exists

If someone is trying to brute-force your master password (trying thousands of combinations), the vault nukes itself after 20 failures. This makes offline brute-force attacks pointless — there's nothing left to decrypt.

> ⚠️ **Warning:** This also means if YOU forget your password and keep guessing, your data WILL be destroyed after 20 wrong tries. Choose your master password wisely.

---

## 🔄 Vault Reset

You can manually reset your vault from the main menu (option 6). This **permanently deletes all data** and lets you start fresh.

### How It Works

```
Your choice: 6

⚠️  WARNING: This will PERMANENTLY delete ALL your vault data!
All passwords, categories, and settings will be erased.
Are you sure you want to reset everything? (y/n): y
Type 'RESET' to confirm: RESET

🔄 Vault has been completely reset.
ℹ️  All passwords and settings have been erased.
ℹ️  Run PyPassVault again to create a new vault.
```

- Requires **double confirmation** — first y/n, then typing `RESET`
- Deletes everything in `~/.pypassvault/`
- After reset, running PyPassVault again will prompt you to create a new vault

---

## Test Output

```bash
$ python tests.py

Testing encryption...
  PASS: Key is 32 bytes (256 bits)
  PASS: Encrypted data is not empty
  PASS: Encrypted != original
  PASS: Decrypted matches original
  PASS: Wrong key raises error

Testing vault...
  PASS: Vault file created
  PASS: Correct password unlocks vault
  PASS: Wrong password rejected

Testing password storage...
  PASS: Password stored and retrieved
  PASS: Username matches
  PASS: Password matches
  PASS: Multiple entries stored
  PASS: Category listed
  PASS: Password deleted
  PASS: Other entries still exist

Testing password generator...
  PASS: Generated password correct length
  PASS: Two passwords are different
  PASS: Short password works

Testing brute-force defense...
  PASS: Initial failed attempts is 0
  PASS: Failed attempts incremented to 2
  PASS: Failed attempts reset to 0
  PASS: Data exists before nuke
  PASS: 19 failed attempts tracked
  PASS: 20th wrong attempt returns None
  PASS: Vault directory destroyed after self-destruct

Testing vault reset...
  PASS: Vault exists before reset
  PASS: Vault directory gone after reset

===================================
  Results: 27 passed, 0 failed
===================================
```

---

## Security Notes

- Uses **PBKDF2** with 100,000 iterations to slow down brute-force attacks
- Uses **AES-256-GCM** for authenticated encryption
- Each encrypt call uses a **fresh random nonce** (12 bytes)
- Master password is **never stored** — only a verification token encrypted with it
- Password generation uses Python's `secrets` module (cryptographically secure)
- All data stays **local** — nothing is sent anywhere
- **Brute-force self-destruct** — 20 consecutive wrong passwords permanently destroys all vault data
- **Failed attempt counter persists** across sessions — restarting the app doesn't reset it
- **Successful login resets** the attempt counter to 0

---

## License

Do whatever you want with it. It's a learning project. 🎓

## Personal Message 

This project has been made with AI assistance not fully AI made i wrote most of the code myself did some bugfixing , ran testcases , naming and commenting and some refinements with AI. hEhE we have to upskill with AI right :)