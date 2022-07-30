from io import BytesIO
import re

from numpy import byte
if __name__ == '__main__':
    from mutator_base import MutatorBase
else:
    from mutators import MutatorBase
import random

SOI = b'\xff\xd8'
EOI = b'\xff\xd9'
SOF_MATCHER = b'\xff[\xc0-\xc3\xc5-\xc7\xc9=\xcb\xcd-\xcf]'
DHT = b'\xff\xc4'
DQT = b'\xff\xdb'
DRI = b'\xff\xdd'
SOS = b'\xff\xda'
COM = b'\xff\xfe'


class JpegMutator(MutatorBase):

    def __init__(self, seed):
        super().__init__()
        self.dct_type = ''
        self.shape = [0, 0]
        self._body = None
        self._huffman_tables = []
        self._quantization_tables = []
        self._markers = []
        self._comments = []
        self._application_meta = {}
        self._seed = seed
        self._sof_info = {}
        self.parse(seed)

    def parse(self, seed: bytes):
        header, _, body = seed.partition(SOS)
        matches = re.finditer(self.marker_matcher, header)
        self._body = body[:-2]
        self._huffman_tables = []
        self._quantization_tables = []
        self._markers = []
        self._comments = []
        self._application_meta = {}
        for m in matches:
            lo, hi = m.span()
            marker = header[lo:hi]
            marker_len = None
            marker_content = None
            self._markers.append(marker)
            # extract header content
            if marker != DRI:
                marker_len = int.from_bytes(header[hi:hi + 2], 'big') - 2
                marker_content = header[hi + 2:hi + 2 + marker_len]
            if re.match(SOF_MATCHER, marker):
                height, width = self.parse_sof(marker_content)
                print(f"Parsed SOF: {width}x{height}")
            elif marker == DHT:
                print(f"Parsed huffman table at {m.span()[0]}")
                table = self.parse_huffman_table(marker_content)
                self._huffman_tables.append(table)
            elif marker == DQT:
                table = self.parse_dqt(marker_content)
                self._quantization_tables.append(table)
                print(f"Parsed quantization table at {m.span()[0]}")
            elif marker == DRI:
                self._restart_interval = int.from_bytes(
                    header[lo + 2:lo + 4], 'big')
                print(
                    f"Parsed restart interval at {m.span()[0]} : {self._restart_interval}"
                )
            elif re.match(br'\xff[\xe0-\xe9\xea-\xef]', marker):
                print(
                    f"Parsed application specific marker {marker} at {m.span()[0]}"
                )
                index = int.from_bytes(marker, 'big') - 0xffe0
                self._application_meta[index] = marker_content
            elif marker == COM:
                self._comments.append(marker_content)

        marker = SOS
        marker_len = int.from_bytes(body[0:2], 'big') - 2
        print(marker_len)
        sos_content = body[2:2 + 10]
        self._sos_info = self.parse_sos(sos_content)
        self._body = body[2 + 10:-2]
        print(f"marker len(body): {marker_len}")

    def parse_sof(self, marker_content):
        self._sof_info['precision'] = marker_content[0]
        self._sof_info['n_components'] = marker_content[5]
        self._sof_info['components'] = []
        color_info = marker_content[6:]
        for i in range(marker_content[5]):
            component = {}
            component['id'] = color_info[3 * i]
            component['scale'] = [
                color_info[1 + 3 * i] >> 4,
                color_info[1 + 3 * i] & 0x0f,
            ]
            component['dqt_index'] = color_info[2 + 3 * i]
            self._sof_info['components'].append(component)
        height = int.from_bytes(marker_content[1:3], 'big')
        width = int.from_bytes(marker_content[3:5], 'big')
        self._height = height
        self._width = width
        return height, width

    def assemble_sof(self):
        res = b''
        res += self._sof_info['precision'].to_bytes(1, 'big')
        res += self._height.to_bytes(2, 'big')
        res += self._width.to_bytes(2, 'big')
        res += self._sof_info['n_components'].to_bytes(1, 'big')
        for i in range(self._sof_info['n_components']):
            component = self._sof_info['components'][i]
            component_bytes = b''
            component_bytes += component['id'].to_bytes(1, 'big')
            component_bytes += ((component['scale'][1] << 4) +
                                component['scale'][0]).to_bytes(1, 'big')
            component_bytes += component['dqt_index'].to_bytes(1, 'big')
            res += component_bytes
        return res

    def parse_huffman_table(self, content: bytes):
        table = {}
        table['class'] = content[0] >> 4
        table['destination'] = content[0] & 0x0f
        table['encodings'] = []
        code_by_size = content[1:17]
        encodings = content[17:]
        lo, hi = 0, 0
        for qty in code_by_size:
            if qty == 0:
                table['encodings'].append(b'')
            else:
                hi += qty
                table['encodings'].append(encodings[lo:hi])
                lo = hi
        return table

    def assemble_huffman_table(self, table: dict):
        raw = b''
        raw += ((table['class'] << 4) + table['destination']).to_bytes(
            1, 'big')
        code_by_size = b''
        encodings = b''
        for e in table['encodings']:
            code_by_size += len(e).to_bytes(1, 'big')
            if len(e) > 0:
                encodings += e
        return raw + code_by_size + encodings

    def parse_dqt(self, content: bytes):
        res = {}
        res['id'] = content[0]
        res['table'] = [content[1 + i * 8:1 + i * 8 + 8] for i in range(8)]
        return res

    def assemble_dqt(self, table):
        res = b''
        res += table['id'].to_bytes(1, 'big')
        res += b''.join(table['table'])
        return res

    def parse_sos(self, content):
        res = {}
        res['n_components'] = content[0]
        res['components'] = []
        for i in range(res['n_components']):
            component = {}
            component['id'] = content[1 + i * 2]
            component['dc'] = content[1 + i * 2 + 1] >> 4
            component['ac'] = content[1 + i * 2 + 1] & 0x0f
            res['components'].append(component)
        res['spectral_select'] = [content[-3], content[-2]]
        res['successive_approx'] = content[-1]
        return res

    def assemble_sos(self, content):
        res = b''
        res += content['n_components'].to_bytes(1, 'big')
        for i in range(content['n_components']):
            component = content['components'][i]
            res += component['id'].to_bytes(1, 'big')
            res += ((component['dc'] << 4) + component['ac']).to_bytes(
                1, 'big')
        res += content['spectral_select'][0].to_bytes(1, 'big')
        res += content['spectral_select'][1].to_bytes(1, 'big')
        res += content['successive_approx'].to_bytes(1, 'big')
        return res

    def _mutate_change_cell_in_dqt(self):
        table_index = random.randint(0, len(self._quantization_tables) - 1)
        row_index = random.randint(0, 7)
        col_index = random.randint(0, 7)
        print(self._quantization_tables[table_index]['table'], flush=True)
        row = self._quantization_tables[table_index]['table'][row_index]
        self._quantization_tables[table_index]['table'][
            row_index] = row[:col_index] + random.randbytes(
                1) + row[col_index + 1:]

    @property
    def marker_matcher(self):
        markers = [
            SOF_MATCHER,
            DHT,
            DQT,
            DRI,
            SOS,
            br'\xff[\xe0-\xe9\xea-\xef]',
            COM,
        ]
        return re.compile(b'|'.join(markers), re.MULTILINE)

    def format_output(self, mutated: bytes = b''):
        header = b""
        dht_index = 0
        dqt_index = 0
        comment_index = 0
        for marker in self._markers:
            if re.match(SOF_MATCHER, marker):
                sof_bytes = self.assemble_sof()
                length = len(sof_bytes) + 2
                header += marker + length.to_bytes(2, 'big')
                header += sof_bytes
            elif marker == DHT:
                table = self._huffman_tables[dht_index]
                table_bytes = self.assemble_huffman_table(table)
                length = len(table_bytes) + 2
                header += marker + length.to_bytes(2, 'big')
                header += table_bytes
                dht_index += 1
            elif marker == DQT:
                table = self._quantization_tables[dqt_index]
                table_bytes = self.assemble_dqt(table)
                length = len(table_bytes) + 2
                header += marker + length.to_bytes(2, 'big')
                header += table_bytes
                dqt_index += 1
            elif marker == DRI:
                header += marker + int.to_bytes(self._restart_interval, 2,
                                                'big')
            elif re.match(br'\xff[\xe0-\xe9\xea-\xef]', marker):
                index = int.from_bytes(marker, 'big') - 0xffe0
                length = len(self._application_meta[index]) + 2
                header += marker + length.to_bytes(2, 'big')
                header += self._application_meta[index]
            elif marker == COM:
                length = len(self._comments[comment_index]) + 2
                header += marker + length.to_bytes(2, 'big')
                header += self._comments[comment_index]
                comment_index += 1

        sos = self.assemble_sos(self._sos_info)
        sos_len = len(sos) + 2
        return SOI + header + SOS + sos_len.to_bytes(
            2, 'big') + sos + self._body + EOI


if __name__ == '__main__':

    with open('./tests/jpg1.txt', 'rb') as f:
        original = f.read()
        m = JpegMutator(original)

        formatted = m.format_output(b"")
        print(formatted == original)
