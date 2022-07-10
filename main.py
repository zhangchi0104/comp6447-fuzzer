from random import random
from RandomFuzzer import RandomFuzzer
from ProgramRunner import ProgramRunner
import sys


def fuzzing(program: str = "./test", min_length: int = 10, max_length: int = 100, trials: int = 10):
    random_fuzzer = RandomFuzzer(min_length=min_length, max_length=max_length)
    p = ProgramRunner(program)

    for i in range(trials):
        print(random_fuzzer.run(p)[1])


if __name__ == "__main__":
    fuzzing(sys.argv[1], min_length=10, max_length=5000, trials=100)
    

