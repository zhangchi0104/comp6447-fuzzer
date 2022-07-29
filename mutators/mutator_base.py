from copy import deepcopy
import random
import pwnlib.util.fiddling as bits
from typing import Tuple, Optional


class MutatorBase(object):
    """
    MutatorBase is the base class for all Mutators, it has predfined mutation
    methods at byte/bit level. It uses generator pattern that will yield an 
    valid ouput derived from seed by calling `next`.
    
    For mutators of other filetypes, simply override `__init__`, `format_output`
    and other mutator methods. mutator methods start with `_mutate_` that will be
    automatically added to `_mutate_methods`, you can also override `self._mutate_methods`
    in subtypes constructors 

    """

    def __init__(self):
        """
        the constructor

        initializes _mutate_methods, subtypes wishes to setup 
        _mutate_methods should invoke this constructor

        Args:
            seed (byte): the seed input

        """

        def is_mutate_method(name: str):
            return name.startswith("_mutate_")

        mutate_methods_iter = filter(is_mutate_method, dir(self))
        self._mutate_methods = [
            getattr(self, method_name) for method_name in mutate_methods_iter
        ]

    def __iter__(self):
        return self

    def __next__(self) -> bytes:
        """
        Method for generating mutated inputs
        It generates inputs from `self._mutate_methods.
        and formats the generated input by calling `self.format_output`
        """
        choice = random.choice(self._mutate_methods)
        new_content = choice()
        return self.format_output(new_content)

    # Common underlying mutators
    @classmethod
    def _flip_random_bit(cls, sample: bytes) -> bytes:
        """
        Low level bit mutation, chooses a random bit in the sample and flip it
        (i.e., 1 -> 0 or 0 -> 1)
        
        Args:
            sample (bytes): the input to be mutated

        Returns:
            the mutated bytes
        """
        pos = random.randint(0, len(sample) - 1)
        sample_bits = bits.bits(sample)
        pos = random.randint(0, len(sample_bits) - 1)
        sample_bits[pos] = 1 - sample_bits[pos]
        return bits.unbits(sample_bits)

    @classmethod
    def _reverse_bits(cls, sample: bytes) -> bytes:
        """
        Low level bit mutation, flips all the btis in `sample`
        (i.e. 0b0011 -> 0b1100)

        Args:
            sample (bytes): the input to be mutated

        Returns:
            the mutated bytes
        """
        return bits.bitswap(sample)

    @classmethod
    def _swap_bits(cls, sample_a: bytes,
                   sample_b: bytes) -> Tuple[bytes, bytes]:
        """
        low level bits mutations swaps two bits in two different samples

        Args:
            sample_a: input to be swapped
            sample_b: input to be swapped

        Returns:
            bit-swapped samples
        """
        bits_a, bits_b = bits.bits(sample_a), bits.bits(sample_b)
        pos_a = random.randint(0, len(bits_a) - 1)
        pos_b = random.randint(0, len(bits_b) - 1)
        tmp = bits_a[pos_a]
        bits_a[pos_a] = bits_b[pos_b]
        bits_b[pos_b] = tmp
        return bits.unbits(bits_a), bits.unbits(bits_b)

    @classmethod
    def _alter_random_byte(cls, sample: bytes) -> bytes:
        """
        low level byte mutation, replacing a byte in sample with a random value
        Args:
            sample (bytes): bytes to be mutated

        Returns:
            mutated bytes
        """
        pos = random.randint(0, len(sample) - 1)
        new_byte = random.randint(0, 0xff).to_bytes(1, 'little')
        return sample[:pos] + new_byte + sample[pos + 1:]

    @classmethod
    def _insert_byte(cls, sample: bytes, pos: Optional[int] = None) -> bytes:
        """
        low level byte mutation, insert a byte into sample
        Args:
            sample (bytes): bytes to be mutated
            pos (int): position of the byte

        Returns:
            mutated bytes
        """
        return cls._insert_multiple_bytes(sample, 1, pos)

    @classmethod
    def _delete_byte(cls, sample: bytes) -> bytes:
        """
        low level byte mutation, remove a byte in sample
        Args:
            sample: bytes to be mutated

        Returns:
            mutated bytes
        """
        pos = random.randint(0, len(sample) - 1)
        return sample[:pos] + sample[pos + 1:]

    @classmethod
    def _insert_multiple_bytes(cls,
                               sample: bytes,
                               n_bytes: Optional[int] = None,
                               pos: Optional[int] = None) -> bytes:
        """
        low level byte mutation, insert `n_bytes` of random bytes into sample
        at index `pos`

        Note: the process is very slow if n_bytes is too large
        Args:
            sample (bytes): bytes to be mutated
            n_bytes(int):
            pos (int): position of the byte, default None

        Returns:
            mutated bytes
        """
        if n_bytes is None:
            n_bytes = random.randint(1, 0xFFFF)

        if pos is None:
            pos = random.randint(0, len(sample) - 1)

        new_bytes = b''

        for _ in range(n_bytes):
            new_bytes += random.randint(0, 0xFF).to_bytes(1, 'little')

        return sample[:pos] + new_bytes + sample[pos:]

    def format_output(self, mutable_content: bytes) -> bytes:
        """
        formats the output, this method will be called before generating the mutated file

        Subtypes must override this method
        """
        raise NotImplementedError(
            "format_output(mutable_content: bytes) -> bytes not implemented")
