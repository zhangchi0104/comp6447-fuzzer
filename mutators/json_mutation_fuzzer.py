from copy import deepcopy
import json
import random
import pwnlib.util.fiddling as bits

def generate(size: int):
    ''' Generate JSONs within JSON '''
    badJson = {}

    currJson = {}
    for i in range(size):
        currJson[str(i)] = i

    badJson[str(random.randint(0,9))] = json.dumps(currJson) * size
    
    return json.dumps(badJson)

class jsonMutationFuzzer(object):
  def __init__(self, seed):
      """
      args:
          seed: the seed csv bytes to mutate from
      """
      self._content = seed
  
  def _bit_flip(self):
      sampleInput = self._content.decode()
  
      for _ in range(0, 500):
          # convert the input into a bytearray
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

  def fuzzJson(self):
    
    for i in range(10):
        badJson = generate(i).replace('\\"',"\"")
    mutatedInput = bytearray(badJson, 'UTF-8')
    return mutatedInput
  
  
  def __iter__(self):
      return self

  def __next__(self):
      # randomly select a mutations methods
      # inspired from ziqi's code
      choice = random.choice([
          self._bit_flip,
          self.fuzzJson
          # self._delete_random_byte,
          # self._empty_csv_random_rows,
          # self._csv_random_rows,
          # self._csv_magic_rows
      ])
      # make mutation
      raw = choice()
      # construct the csv file body
      return raw