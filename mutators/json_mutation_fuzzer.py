from copy import deepcopy
import json
import random
import pwnlib.util.fiddling as bits
from .mutator_base import MutatorBase


def generate(size: int):
    ''' Generate JSONs within JSON '''
    badJson = {}

    currJson = {}
    for i in range(size):
        currJson[str(i)] = i

    badJson[str(random.randint(0, 9))] = json.dumps(currJson) * size

    return json.dumps(badJson)


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

    def _mutate_fuzzJson(self):

        for i in range(10):
            badJson = generate(i).replace('\\"', "\"")
        mutatedInput = bytearray(badJson, 'UTF-8')
        return mutatedInput

    def format_output(self, raw):
        # construct the csv file body
        return raw