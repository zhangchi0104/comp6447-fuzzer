# from copy import deepcopy
# from .mutator_base import MutatorBase
# import random
# import pwnlib.util.fiddling as bits


# class PlaintextFuzzer(MutatorBase):
#     """
#         A fuzzer randomly generates inputs based on mutation of the seeds
#         It implements python's generator
        
#         Attributes:
#             _content: lines of strings seperated by newline
#     """
#     def __init__(self, seed: bytes):
#         """
#         Args:
#             seed: a line of string or strings seperated by newline
#         """
#         super().__init__()
#         content = seed.splitlines()
#         # seed seperated in a list by newline
#         self._content = [line for line in content]
#         # first line of seed
#         self._header = content[0]
#         # number of lines in seed
#         self.numLines = len(content)
#         # mutation methods
#         self.mutators = ["nothing", "addChar", "null", "newline", "format", "ascii", "largeNeg", "largePos", "zero"]
#         # a list of malicious bytes
#         self.badBytes = self.getBadBytes()
        
#     # Append character padding
#     def _mutate_add_char(self):
#         content = deepcopy(self._content)
#         for line in content:
#             line += "A" * 2000
#         return content
        
    
#     def format_output(self, raw):
#         # construct the plaintext file body
#         all_bytes = self._header + b'\n' + bytes(b'\n'.join(row for row in raw))
#         # replace null bytes with non-null to avoid format issues
#         all_bytes = all_bytes.replace(
#             b'\x00',
#             random.randint(0x1, 0xff).to_bytes(1, 'little'))
#         return all_bytes
    
    
    
        
        
        