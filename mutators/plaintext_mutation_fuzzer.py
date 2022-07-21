from copy import deepcopy
from .mutator_base import MutatorBase
import random
import pwnlib.util.fiddling as bits


class PlaintextFuzzer(MutatorBase):
    """
        A fuzzer randomly generates inputs based on mutation of the seeds
        It implements python's generator
        
        Attributes:
            _content: lines of strings seperated by newline
    """
    def __init__(self, seed: bytes):
        """
        Args:
            seed: a line of string or strings seperated by newline
        """
        super().__init__(seed)
        content = seed.splitlines()
        # seed seperated in a list by newline
        self._content = [line for line in content]
        # first line of seed
        self._header = content[0]
        # number of lines in seed
        self.numLines = len(content)
        # mutation methods
        # self.mutators = ["nothing", "addChar", "null", "newline", "format", "ascii", "largeNeg", "largePos", "zero"]
        # a list of malicious bytes
        # self.badBytes = self.getBadBytes()
        
    # Append character padding
    def _mutate_add_char(self):
        content = deepcopy(self._content)
        for line in content:
            line += b'A' * 2000
        return content
    
    # Append null characters
    def _mutate_null(self):
        content = deepcopy(self._content)
        for line in content:
            line += b'0' * 2000
        return content
    
    # Append newlines
    def _mutate_newlines(self):
        content = deepcopy(self._content)
        for line in content:
            line += b'\n' * 2000
        return content
    
    # Append format string
    def _mutate_format_string(self):
        content = deepcopy(self._content)
        for line in content:
            line += b'%s%x%p%n' * 2000
        return content
    
    # Append ascii characters
    def _mutate_ascii(self):
        content = deepcopy(self._content)
        for line in content:
            for count in range(128):
                line += bytes(chr(count), encoding= "utf-8")
        return content
    
    # Change seed to a large negative number
    def _mutate_large_negNum1(self):
        content = deepcopy(self._content)
        for line in content:
            line = -999999999999999999
        return content
    
    # same as above but keep the header
    def _mutate_large_negNum2(self):
        content = deepcopy(self._content)
        for line in content[1: ]:
            line = -999999999999999999
        return content
    
    # same as negNum1 but with positive num
    def _mutate_large_num1(self):
        content = deepcopy(self._content)
        for line in content:
            line = 9999999999999999999999
        return content
    
    # same as above but keep the header
    def _mutate_large_num2(self):
        content = deepcopy(self._content)
        for line in content[1: ]:
            line = 9999999999999999999999
        return content
    
    
    
    
    
    
    
    
    
    
    
    def format_output(self, raw):
        # construct the plaintext file body
        # all_bytes = bytes(b'\n'.join(row for row in raw))
        all_bytes = bytes(b'\n'.join(line for line in raw))
        # replace null bytes with non-null to avoid format issues
        all_bytes = all_bytes.replace(
            b'\x00',
            random.randint(0x1, 0xff).to_bytes(1, 'little'))
        return all_bytes
    
    
    
        
        
        