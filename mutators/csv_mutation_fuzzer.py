from copy import deepcopy
from .mutator_base import MutatorBase
import random
import pwnlib.util.fiddling as bits


class CsvMutator(MutatorBase):
    """
        A fuzzer randomly generates inputs based on mutation of the seeds
        It implements python's generator
        
        Attributes:
            _content: 2D array that represents the cells of a csv
            shape: the dimensions of the csv (rows x cols)

    """

    def __init__(self, seed: bytes):
        """
        Args:
            seed: the seed csv bytes to mutate from
        """
        super().__init__(seed)
        content = seed.splitlines()
        self._content = [[cell for cell in line.split(b',')]
                         for line in content[1:]]
        self._header = content[0]
        self.shape = (len(content[1:]), len(content[0].split(b',')))

    def _mutate_flip_random_bit(self):
        content = deepcopy(self._content)
        # select a random cell
        row = random.randint(0, self.shape[0] - 1)
        col = random.randint(0, self.shape[1] - 1)
        # flip a bit
        new_cell = self._flip_random_bit(content[row][col])
        # replace with the mutated cell
        content[row][col] = new_cell
        return content

    def _mutate_reverse_random_cell(self):
        """
        swap all bits in a random cell
        1100 -> 0011
        """
        content = deepcopy(self._content)
        # select a random cell
        row = random.randint(0, self.shape[0] - 1)
        col = random.randint(0, self.shape[1] - 1)
        content[row][col] = self._reverse_bits(content[row][col])
        return content

    def _mutate_swap_random_bits(self):
        content = deepcopy(self._content)
        # select two cells
        row_a, col_a = self._select_random_cell()
        row_b, col_b = self._select_random_cell()
        cell_a = self._content[row_a][col_a]
        cell_b = self._content[row_b][col_b]
        # swap them
        new_cell_a, new_cell_b = self._swap_bits(cell_a, cell_b)
        content[row_a][col_a] = new_cell_a
        content[row_b][col_b] = new_cell_b
        return content

    def _select_random_cell(self):
        row = random.randint(0, self.shape[0] - 1)
        col = random.randint(0, self.shape[1] - 1)
        return row, col

    def _csv_magic_rows(self):
        cell_size = 0x1
        return [
            [b'\x80' * cell_size] * self.shape[1],
        ]

    def _mutate_replace_random_byte(self):
        """
        randomly change a byte in a cell
        """
        content = deepcopy(self._content)
        row, col = self._select_random_cell()
        cell = content[row][col]
        content[row][col] = self._alter_random_byte(cell)
        return content

    def _mutate_insert_random_bytes(self):
        content = deepcopy(self._content)
        # select a cell
        row, col = self._select_random_cell()
        cell = content[row][col]
        # replace the original cell
        content[row][col] = self._insert_multiple_bytes(cell)
        return content

    def _mutate_delete_random_byte(self):
        content = deepcopy(self._content)
        # select a random cell
        row, col = self._select_random_cell()
        cell = content[row][col]
        # select a random byte
        content[row][col] = self._delete_byte(cell)
        return content

    # more fuzzing methods
    def _mutate_insert_multiple_rows(self):
        """attempt to overflow with large lines of input"""
        return [[
            random.randint(0, 0xFFFFFFFF).to_bytes(4, 'little')
            for _ in range(self.shape[1])
        ] for _ in range(2000)]

    def format_output(self, raw):
        # construct the csv file body
        all_bytes = self._header + b'\n' + bytes(b'\n'.join(b','.join(row)
                                                            for row in raw))
        # replace null bytes with non-null to avoid format issues
        all_bytes = all_bytes.replace(
            b'\x00',
            random.randint(0x1, 0xff).to_bytes(1, 'little'))
        return all_bytes
