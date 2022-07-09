import random


def delete_random_character(s: str) -> str:
    """Return s with a random character deleted"""
    if s == "":
        return s

    pos = random.randint(0, len(s) - 1)

    return s[:pos] + s[pos + 1:]


def insert_random_character(s: str) -> str:
    """Return s with a random character inserted"""
    pos = random.randint(0, len(s))
    random_character = chr(random.randrange(32, 127))

    return s[:pos] + random_character + s[pos:]


def flip_random_character(s):
    """Return s with a random bit flipped in a random position"""
    if s == "":
        return s

    pos = random.randint(0, len(s) - 1)
    c = s[pos]
    bit = 1 << random.randint(0, 6)
    new_c = chr(ord(c) ^ bit)
    return s[:pos] + new_c + s[pos + 1:]


# More mutation methods can be added below
# .......


def mutate(s: str) -> str:
    """Return s with a random mutation applied"""
    mutators = [
        delete_random_character,
        insert_random_character,
        flip_random_character
        # more ...
    ]
    mutator = random.choice(mutators)
    return mutator(s)