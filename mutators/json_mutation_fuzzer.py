from copy import deepcopy
from .mutator_base import MutatorBase
import json
import random
import pwnlib.util.fiddling as bits

class jsonMutationFuzzer(MutatorBase):
  def __init__(self, seed):
      """
      args:
          seed: the seed csv bytes to mutate from
      """
      super().__init__(seed)
      self._content = json.loads(seed)
      
  
  def _mutate_bit_flip(self):
      sampleInput = json.dumps(self._content)
      pos = random.randint(0, len(sampleInput) - 1)
      
      for _ in range(0, 500):
          # convert the input into a bytearray
          #print(sampleInput)
          b = bytearray(sampleInput, 'UTF-8')
  
          # Then we search through the entire bytearray created, and randomly
          # flip some of the bits
          for i in range(0, len(b)):
              if random.randint(0, 20) == 1:
                  b[i] ^= random.getrandbits(7)
  
      # Once we have flipped the bits, we want to decode this back into a string
      # that can be passed in as input to the binary
      #mutatedInput = b.decode('ascii').strip()
      return b
      
  def _mutate_add_known_int(self):
      int_vals = [
                	0xFF,
                	0x7F,
                	0x00,
                	0xFFFF,
                	0x0000,
                	0xFFFFFFFF,
                	0x00000000,
                	0x80000000,
                	0x40000000,
                	0x7FFFFFFF
                	]
                	
      sampleInput = self._content
      pos = random.randint(0, len(sampleInput) - 1)
      picked_int = random.choice(int_vals)
      
      for i, member in enumerate(sampleInput):
          if i == pos:
              sampleInput[member] = picked_int
        
  
      # Once we have flipped the bits, we want to decode this back into a string
      # that can be passed in as input to the binary
      #mutatedInput = b.decode('ascii').strip()
      return json.dumps(sampleInput).encode()

  def format_output(self, raw):
        # construct the csv file body
        return raw