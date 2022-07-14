from copy import deepcopy
import random
import pwnlib.util.fiddling as bits


class CsvMutationFuzzer(object):
    """
        A fuzzer randomly generates inputs based on mutation of the seeds
        It implements python's generator
        
        Attributes:
            _content: 2D array that represents the cells of a csv
            shape: the dimensions of the csv (rows x cols)

    """

    def __init__(self, seed: bytes):
        """
        args:
            seed: the seed csv bytes to mutate from
        """
        content = seed.splitlines()
        self._content = [[cell for cell in line.split(b',')]
                         for line in content[1:]]
        self._header = content[0]
        self.shape = (len(content[1:]), len(content[0].split(b',')))

    def _flip_random_bit(self):
        content = deepcopy(self._content)
        # select a random cell
        row = random.randint(0, self.shape[0] - 1)
        col = random.randint(0, self.shape[1] - 1)
        # convert that cell to bits
        cell_bits = bits.bits(content[row][col])
        pos = random.randint(0, len(cell_bits) - 1)
        # flip a bit
        cell_bits[pos] = 1 - cell_bits[pos]
        # replace with the mutated cell
        content[row][col] = bits.unbits(cell_bits)
        return content

    def _swap_random_cell(self):
        """
        swap all bits in a random cell
        1100 -> 0011
        """
        content = deepcopy(self._content)
        # select a random cell
        row = random.randint(0, self.shape[0] - 1)
        col = random.randint(0, self.shape[1] - 1)
        content[row][col] = bits.bitswap(content[row][col])
        return content

    def swap_random_bits(self):
        content = deepcopy(self._content)
        # select two cells
        row_a, col_a = self._select_random_cell()
        row_b, col_b = self._select_random_cell()
        cell_a = self._content[row_a][col_a]
        cell_b = self._content[row_b][col_b]
        # convert them to bits
        bits_a = bits.bits(cell_a)
        bits_b = bits.bits(cell_b)
        # select two bits
        pos_a = random.randint(0, len(bits_a) - 1)
        pos_b = random.randint(0, len(bits_b) - 1)
        # swap them
        tmp = bits_a[pos_a]
        bits_a[pos_a] = bits_b[pos_b]
        bits_b[pos_b] = tmp
        content[row_a][col_a] = bits.unbits(bits_a)
        content[row_b][col_b] = bits.unbits(bits_b)
        return content

    def _select_random_cell(self):
        row = random.randint(0, self.shape[0] - 1)
        col = random.randint(0, self.shape[1] - 1)
        return row, col

    def _empty_csv_random_rows(self):
        # does not work well
        return [[b'\x01' for _ in range(self.shape[1])]
                for _ in range(random.randint(1, 0xFFFFF))]

    def _csv_random_rows(self):
        "crete a random csv body"
        return [[
            random.randint(0, 0xFFFFFFFF).to_bytes(4, 'little')
            for _ in range(self.shape[1])
        ] for _ in range(random.randint(1, 0xF))]

    def _csv_magic_rows(self):
        cell_size = 0x1
        return [
            [b'\x80' * cell_size] * self.shape[1],
        ]

    def _mutate_random_byte(self):
        """
        randomly change a byte in a cell
        """
        content = deepcopy(self._content)
        row, col = self._select_random_cell()
        cell = content[row][col]
        rand_byte = random.randint(0, 0xFFFFFFFF).to_bytes(
            random.randint(4, 0x6f), 'little')
        byte_index = random.randint(0, len(cell) - 1)
        content[row][col] = cell[:byte_index] + rand_byte + cell[byte_index +
                                                                 1:]
        return content

    def _insert_random_bytes(self):
        content = deepcopy(self._content)
        # select a cell
        row, col = self._select_random_cell()
        cell = content[row][col]
        # generate new bytes
        rand_byte = random.randint(0, 0xFFFFFFFF).to_bytes(
            random.randint(4, 0x6f), 'little')
        byte_index = random.randint(0, len(cell) - 1)
        # replace the original cell
        content[row][col] = cell[:byte_index] + rand_byte + cell[byte_index:]
        return content

    def _delete_random_byte(self):
        content = deepcopy(self._content)
        # select a random cell
        row, col = self._select_random_cell()
        cell = content[row][col]
        # select a random byte
        byte_index = random.randint(0, len(cell) - 1)
        # remove that byte
        content[row][col] = cell[:byte_index] + cell[byte_index + 1:]
        return content

    # more fuzzing methods
    def _insert_multiple_rows(self):
        """attempt to overflow with large lines of input"""
        return [[
            random.randint(0, 0xFFFFFFFF).to_bytes(4, 'little')
            for _ in range(self.shape[1])
        ] for _ in range(2000)]

    def _insert_random_multiple_bytes(self):
        """attempt to overflow with a large chunk of bytes for a random cell"""
        content = deepcopy(self._content)
        # select a cell
        row, col = self._select_random_cell()
        cell = content[row][col]
        # generate new bytes
        rand_byte = random.randint(0, 0xFFFFFFFF).to_bytes(
            random.randint(4, 0x6f), 'little')
        byte_index = random.randint(0, len(cell) - 1)
        # replace the original cell
        content[row][
            col] = cell[:byte_index] + 1000 * rand_byte + cell[byte_index:]
        return content

    def _insert_multiple_bytes(self):
        """attempt to overflow with large a chunk of bytes for each cell"""
        content = deepcopy(self._content)
        # iterate each cell
        for row in range(self.shape[0] - 1):
            for col in range(self.shape[1] - 1):
                # replace with 1000 random bytes
                rand_byte = random.randint(0, 0xFFFFFFFF).to_bytes(
                    random.randint(4, 0x6f), 'little')
                content[row][col] = 1000 * rand_byte
        return content

    def __iter__(self):
        return self

    def __next__(self):
        # randomly select a mutations methods
        # inspired from ziqi's code
        choice = random.choice([
            self._flip_random_bit, self._swap_random_cell,
            self.swap_random_bits, self._mutate_random_byte,
            self._insert_random_bytes, self._insert_multiple_rows,
            self._insert_random_multiple_bytes, self._insert_multiple_bytes
            # self._delete_random_byte,
            # self._empty_csv_random_rows,
            # self._csv_random_rows,
            # self._csv_magic_rows
        ])
        # make mutation
        raw = choice()
        # construct the csv file body
        all_bytes = self._header + b'\n' + bytes(b'\n'.join(b','.join(row)
                                                            for row in raw))
        # replace null bytes with non-null to avoid format issues
        all_bytes = all_bytes.replace(
            b'\x00',
            random.randint(0x1, 0xff).to_bytes(1, 'little'))
        return all_bytes
