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
        super().__init__()
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
        self.badBytes = self.getBadBytes()

    # Append character padding
    def _mutate_add_char1(self):
        content = deepcopy(self._content)
        for i in range(len(content)):
            content[i] += b'A' * 2000
        return content

    def _mutate_add_char2(self):
        content = deepcopy(self._content)
        for i in range(len(content[1:])):
            content[i + 1] += b'A' * 2000
        return content

    # Append null characters
    def _mutate_null1(self):
        content = deepcopy(self._content)
        for i in range(len(content)):
            content[i] += b'0' * 2000
        return content

    def _mutate_null2(self):
        content = deepcopy(self._content)
        for i in range(len(content[1:])):
            content[i + 1] += b'0' * 2000
        return content

    # Append newlines
    def _mutate_newlines1(self):
        content = deepcopy(self._content)
        for i in range(len(content)):
            content[i] += b'\n' * 2000
        return content

    def _mutate_newlines2(self):
        content = deepcopy(self._content)
        for i in range(len(content[1:])):
            content[i + 1] += b'\n' * 2000
        return content

    # Append format string
    def _mutate_format_string1(self):
        content = deepcopy(self._content)
        for i in range(len(content)):
            content[i] += b'%s' * 2000
        return content

    def _mutate_format_string2(self):
        content = deepcopy(self._content)
        for i in range(len(content[1:])):
            content[i + 1] += b'%s' * 2000
        return content

    # Append ascii characters
    def _mutate_ascii1(self):
        content = deepcopy(self._content)
        for i in range(len(content)):
            for count in range(128):
                content[i] += bytes(chr(count), encoding="utf-8")
        return content

    def _mutate_ascii2(self):
        content = deepcopy(self._content)
        for i in range(len(content[1:])):
            for count in range(128):
                content[i + 1] += bytes(chr(count), encoding="utf-8")
        return content

    # Change seed to a large negative number
    def _mutate_large_negNum1(self):
        content = deepcopy(self._content)
        for i in range(len(content)):
            content[i] = b'-99999999'
        return content

    def _mutate_large_negNum2(self):
        content = deepcopy(self._content)
        for i in range(len(content[1:])):
            content[i + 1] = b'-99999999'
        return content

    # same as negNum1 but with positive num
    def _mutate_large_num1(self):
        content = deepcopy(self._content)
        for i in range(len(content)):
            content[i] = b'99999999'
        return content

    def _mutate_large_num2(self):
        content = deepcopy(self._content)
        for i in range(len(content[1:])):
            content[i + 1] = b'99999999'
        return content

    # # mutate into zero
    def _mutate_zero1(self):
        content = deepcopy(self._content)
        for i in range(len(content[1:])):
            content[i] = b'0'
        return content

    def _mutate_zero2(self):
        content = deepcopy(self._content)
        for i in range(len(content[1:])):
            content[i + 1] = b'0'
        return content

    def _mutate_null1(self):
        content = deepcopy(self._content)
        for i in range(len(content[1:])):
            content[i] = b'\0'
        return content

    def _mutate_null2(self):
        content = deepcopy(self._content)
        for i in range(len(content[1:])):
            content[i] = b'\0'
        return content

    def _mutate_test(self):
        content = deepcopy(self._content)
        for i in range(len(content)):
            content[i] += b'\x04'
        return content

    # helper function
    def getBadBytes(self):
        l = []
        count = 0
        while count <= 127:
            if count < 48 or count > 122:
                l.append(chr(count))
            count += 1
        l = l + ["a", "%s", "-99999999", "99999999"]
        return l

    # mutate a random byte in a list of string
    def _mutate_randomChar(self):
        content = deepcopy(self._content)
        pickLine = random.randint(0, len(content) - 1)
        pickChar = random.randint(0, len(content[pickLine]) - 1)
        pickRandomChar = self.badBytes[random.randint(0,
                                                      len(self.badBytes) - 1)]
        content[pickLine] = content[pickLine][:pickChar] + bytes(
            pickRandomChar,
            encoding="utf-8") + content[pickLine][pickChar + 1:]
        return content

    def format_output(self, raw):
        # construct the plaintext file body
        # all_bytes = bytes(b'\n'.join(row for row in raw))
        all_bytes = bytes(b'\n'.join(row for row in raw))
        # replace null bytes with non-null to avoid format issues
        all_bytes = all_bytes.replace(
            b'\x00',
            random.randint(0x1, 0xff).to_bytes(1, 'little'))
        return all_bytes
