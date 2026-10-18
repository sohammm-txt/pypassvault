import secrets
import string


def generate_password(length=16):
    chars = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(chars) for _ in range(length))
    return password


def get_input(prompt, allow_empty=False):
    while True:
        value = input(prompt).strip()
        if value or allow_empty:
            return value
        print("This field can't be empty. Try again.")


def confirm(prompt):
    answer = input(f"{prompt} (y/n): ").strip().lower()
    return answer == "y"
