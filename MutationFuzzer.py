from Fuzzer import Fuzzer
from typing import List
import MutationMethods
import random


class MutationFuzzer(Fuzzer):
    """Base class for mutational fuzzing"""

    def __init__(self, seed: List[str],
                       min_mutations: int = 2,
                       max_mutations: int = 10) -> None:
        """
        Constructor
        'seed' - a list of (input) strings to mutate
        'min_mutations' - the minimum number of mutations to apply
        'max_mutations' - the maximum number of mutations to apply
        """
        self.seed = seed
        self.min_mutations = min_mutations
        self.max_mutations = max_mutations
        self.reset()

    def reset(self) -> None:
        """
        Set population to initial seed
        """
        self.population = self.seed
        self.seed_index = 0

    def mutate(self, inp: str) -> str:
        return MutationMethods.mutate(inp)

    def create_candidate(self) -> str:
        """Create a new candidate by mutating a population member"""
        candidate = random.choice(self.population)
        trials = random.randint(self.min_mutations, self.max_mutations)
        for i in range(trials):
            candidate = self.mutate(candidate)
        return candidate

    def fuzz(self) -> str:
        if self.seed_index < len(self.seed):
            self.inp = self.seed[self.seed_index]
            self.seed_index += 1
        else:
            self.inp = self.create_candidate()
        return self.inp

    def delete_random_character(s: str) -> str:
        """Return s with a random character deleted"""
        if s == "":
            return s

        pos = random.randint(0, len(s) - 1)

        return s[:pos] + s[pos + 1:]


    def insert_random_character(sefl, s: str) -> str:
        """Return s with a random character inserted"""
        pos = random.randint(0, len(s))
        random_character = chr(random.randrange(32, 127))

        return s[:pos] + random_character + s[pos:]


    def flip_random_character(self, s):
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


    def mutate(self, s: str) -> str:
        """Return s with a random mutation applied"""
        mutators = [
            self.delete_random_character,
            self.insert_random_character,
            self.flip_random_character,
            self.
            # more ...
        ]
        mutator = random.choice(mutators)
        return mutator(s)