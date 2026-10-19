import getpass
from vault import (is_vault_created, create_vault, unlock_vault,
                   add_password, get_password, delete_password,
                   list_categories, list_entries, reset_vault,
                   is_reserved_category)
from utils import generate_password, get_input, confirm


def banner():
    print()
    print('=' * 40)
    print('   PyPassVault - Password Manager')
    print('=' * 40)


def menu():
    print()
    print('--- Menu ---')
    print('1. Add password')
    print('2. View password')
    print('3. List entries')
    print('4. Delete password')
    print('5. Generate password')
    print('6. Reset vault')
    print('7. Quit')


def _ask_length():
    raw = input('Length (default 16): ').strip()
    if raw.isdigit() and int(raw) >= 4:
        return int(raw)
    return 16


def main():
    banner()

    if not is_vault_created():
        print('\nNo vault found. Creating one now.')
        pw = getpass.getpass('Master password: ')
        pw2 = getpass.getpass('Confirm: ')

        if pw != pw2:
            print("Passwords don't match.")
            return
        if len(pw) < 4:
            print('Too short, need at least 4 chars.')
            return

        key, salt = create_vault(pw)
        print('Vault created.')
    else:
        pw = getpass.getpass('Master password: ')
        key, salt = unlock_vault(pw)
        if key is None:
            return
        print('Unlocked.')

    while True:
        menu()
        choice = get_input('\n> ')

        if choice == '1':
            cat = get_input('Category (e.g. social, work): ')
            if is_reserved_category(cat):
                print(f"'{cat}' is reserved, pick another name.")
                continue
            name = get_input('Entry name: ')
            user = get_input('Username/email: ')

            if confirm('Generate random password?'):
                length = _ask_length()
                pwd = generate_password(length)
                print(f'Generated: {pwd}')
            else:
                pwd = getpass.getpass('Password: ')

            add_password(cat, name, user, pwd, key)
            print(f"Saved '{name}' in '{cat}'.")

        elif choice == '2':
            cats = list_categories()
            if not cats:
                print('Nothing stored yet.')
                continue

            print(f'Categories: {", ".join(cats)}')
            cat = get_input('Category: ')
            names = list_entries(cat, key)
            if not names:
                print('Empty category.')
                continue

            print(f'Entries: {", ".join(names)}')
            name = get_input('Entry: ')
            entry = get_password(cat, name, key)
            if entry:
                print(f'  User: {entry["username"]}')
                print(f'  Pass: {entry["password"]}')
            else:
                print('Not found.')

        elif choice == '3':
            cats = list_categories()
            if not cats:
                print('Nothing stored yet.')
                continue
            for c in cats:
                names = list_entries(c, key)
                print(f'\n[{c}]')
                for n in names:
                    print(f'  - {n}')

        elif choice == '4':
            cat = get_input('Category: ')
            name = get_input('Entry to delete: ')
            if confirm(f"Delete '{name}' from '{cat}'?"):
                if delete_password(cat, name, key):
                    print('Deleted.')
                else:
                    print('Not found.')

        elif choice == '5':
            length = _ask_length()
            print(f'Password: {generate_password(length)}')

        elif choice == '6':
            print('\nThis will permanently delete all vault data.')
            if confirm('Are you sure?'):
                word = input("Type 'RESET' to confirm: ").strip()
                if word == 'RESET':
                    reset_vault()
                    break
                else:
                    print('Cancelled.')

        elif choice == '7':
            print('Bye.')
            break

        else:
            print('Invalid option.')


if __name__ == '__main__':
    main()
