import getpass
from vault import is_vault_created, create_vault, unlock_vault
from vault import add_password, get_password, delete_password
from vault import list_categories, list_entries
from vault import reset_vault
from utils import generate_password, get_input, confirm


def print_banner():
    print()
    print("=" * 40)
    print("   PyPassVault - Password Manager")
    print("   AES-256 Encrypted Storage")
    print("=" * 40)


def print_menu():
    print()
    print("--- Main Menu ---")
    print("1. Add a password")
    print("2. View a password")
    print("3. List all entries")
    print("4. Delete a password")
    print("5. Generate a password")
    print("6. Reset vault (⚠️  destroys all data)")
    print("7. Exit")


def main():
    print_banner()

    if not is_vault_created():
        print("\nFirst time? Let's create your vault!")
        master_pass = getpass.getpass("Set your master password: ")
        confirm_pass = getpass.getpass("Confirm master password: ")

        if master_pass != confirm_pass:
            print("Passwords don't match. Bye!")
            return

        if len(master_pass) < 4:
            print("Password too short. Use at least 4 characters.")
            return

        key, salt = create_vault(master_pass)
        print("Vault created successfully!")
    else:
        master_pass = getpass.getpass("Enter master password: ")
        key, salt = unlock_vault(master_pass)

        if key is None:
            print("Wrong password! Bye!")
            return

        print("Vault unlocked!")

    while True:
        print_menu()
        choice = get_input("\nYour choice: ")

        if choice == "1":
            category = get_input("Category (e.g. social, work, email): ")
            name = get_input("Entry name: ")
            username = get_input("Username/Email: ")

            if confirm("Generate a random password?"):
                length = input("Password length (default 16): ").strip()
                length = int(length) if length.isdigit() else 16
                password = generate_password(length)
                print(f"Generated: {password}")
            else:
                password = getpass.getpass("Password: ")

            add_password(category, name, username, password, key)
            print(f"Saved '{name}' under '{category}'!")

        elif choice == "2":
            categories = list_categories()
            if not categories:
                print("Vault is empty!")
                continue

            print(f"Categories: {', '.join(categories)}")
            category = get_input("Category: ")
            entries = list_entries(category, key)

            if not entries:
                print("No entries in this category.")
                continue

            print(f"Entries: {', '.join(entries)}")
            name = get_input("Entry name: ")
            entry = get_password(category, name, key)

            if entry:
                print(f"\n  Username: {entry['username']}")
                print(f"  Password: {entry['password']}")
            else:
                print("Entry not found.")

        elif choice == "3":
            categories = list_categories()
            if not categories:
                print("Vault is empty!")
                continue

            for cat in categories:
                entries = list_entries(cat, key)
                print(f"\n[{cat}]")
                for e in entries:
                    print(f"  - {e}")

        elif choice == "4":
            category = get_input("Category: ")
            name = get_input("Entry name to delete: ")

            if confirm(f"Delete '{name}' from '{category}'?"):
                if delete_password(category, name, key):
                    print("Deleted!")
                else:
                    print("Entry not found.")

        elif choice == "5":
            length = input("Password length (default 16): ").strip()
            length = int(length) if length.isdigit() else 16
            print(f"Generated: {generate_password(length)}")

        elif choice == "6":
            print("\n⚠️  WARNING: This will PERMANENTLY delete ALL your vault data!")
            print("All passwords, categories, and settings will be erased.")
            if confirm("Are you sure you want to reset everything?"):
                confirmation = input("Type 'RESET' to confirm: ").strip()
                if confirmation == "RESET":
                    reset_vault()
                    break
                else:
                    print("Reset cancelled.")
            else:
                print("Reset cancelled.")

        elif choice == "7":
            print("Bye! Stay safe!")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
