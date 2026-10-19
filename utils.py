import secrets
import string


def generate_password(length=16):
    if length < 4:
        length = 4

    lower = secrets.choice(string.ascii_lowercase)
    upper = secrets.choice(string.ascii_uppercase)
    digit = secrets.choice(string.digits)
    symbol = secrets.choice(string.punctuation)

    rest_chars = string.ascii_letters + string.digits + string.punctuation
    rest = [secrets.choice(rest_chars) for _ in range(length - 4)]

    pool = [lower, upper, digit, symbol] + rest
    # shuffle so the guaranteed chars aren't always at the start
    result = list(pool)
    for i in range(len(result) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        result[i], result[j] = result[j], result[i]

    return ''.join(result)


def get_input(prompt, allow_empty=False):
    while True:
        value = input(prompt).strip()
        if value or allow_empty:
            return value
        print("Can't be empty.")


def confirm(prompt):
    answer = input(f"{prompt} (y/n): ").strip().lower()
    return answer == 'y'
