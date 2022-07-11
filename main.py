from random import random
from RandomFuzzer import RandomFuzzer
from MutationFuzzer import MutationFuzzer
from ProgramRunner import ProgramRunner
import sys


def fuzzing(program: str = "./test", min_length: int = 10, max_length: int = 100, trials: int = 10):
    inp = open("tests/csv1.txt").read()
    p = ProgramRunner(program)
    mutation_fuzzer = MutationFuzzer(seed=inp)


    for i in range(trials):
        print(mutation_fuzzer.run(p)[1])


if __name__ == "__main__":
    fuzzing("./tests/csv1", min_length=10, max_length=100000, trials=20)
    

