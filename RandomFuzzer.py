from Fuzzer import Fuzzer
from ProgramRunner import ProgramRunner
import random


class RandomFuzzer(Fuzzer):
    """Produce random inputs"""

    def __init__(self, min_length: int = 10, max_length: int = 100, char_start: int = 32, char_range: int = 32) -> None:
        """
        Produce strings of 'min_length' to 'max_length' characters
        in the range ['char_start', 'char_start' + 'char_range']
        """
        self.min_length = min_length
        self.max_length = max_length
        self.char_start = char_start
        self.char_range = char_range

    def fuzz(self) -> str:
        string_length = random.randrange(self.min_length, self.max_length + 1)
        out = ""
        for i in range(0, string_length):
            out += chr(random.randrange(self.char_start, self.char_start + self.char_range))

        return out
        
    