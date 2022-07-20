from os import PathLike
import pwn
import math


class Harness(object):

    def __init__(self, binary: PathLike, seed: PathLike):
        self._binary = binary
        self._seed = seed
