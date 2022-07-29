from statistics import mean

from requests import delete
from mutator_base import MutatorBase
import re
import sys
import zlib


class PdfMutatur(MutatorBase):

    def __init__(self, seed: bytes):
        super().__init__(seed)
        self._stream_objs = {}
        self._seed = seed
        self._objs = {}
        self._version = ""
        self._parse(seed)
        # self._parse_obj(self._raw_objs[1])

    def _parse(self, seed: bytes):
        # parising header
        header, _, content = seed.partition(b'\n')
        matched = re.findall(r'%PDF-(\d.\d)'.encode(), header)[0]
        self._version = matched.decode()

        # parsing content
        begin_matched = re.finditer(
            r'^(\d+) \d obj\r?\n'.encode(),
            content,
            re.MULTILINE,
        )
        end_matched = re.finditer(
            r'endobj\r?\n'.encode(),
            content,
            re.MULTILINE,
        )
        raw_stream_objs = {}
        for beg_m, end_m in zip(begin_matched, end_matched):

            lo = beg_m.end()
            hi = end_m.start()
            id = int(beg_m.group(1))

            chunk = content[lo:hi].strip()
            if chunk.endswith(b'endstream'):
                raw_stream_objs[id] = {
                    "data": chunk,
                    "range": (lo, hi),
                }

        for i, obj in raw_stream_objs.items():

            decoded = self._parse_stream_chunk(obj['data'])

            self._stream_objs[i] = {**decoded, "range": obj['range']}
            print(f"=====Object {i}=====")
            print(f"metadata: {self._stream_objs[i]['metadata']}")
            print(f"range: {self._stream_objs[i]['range']}")
            print(
                f"legnth of stream decoded: {len(self._stream_objs[i]['stream'])}"
            )

    def _parse_stream_chunk(self, obj: bytes):
        header, _, stream = re.split(r'\>\>(\r?\n)? ?stream'.encode(), obj)
        header = header[2:]
        header = b' '.join(header.splitlines())
        header = header.strip()

        metadata = {}
        stream = stream.strip()
        encode_method_matched = re.match(
            rb"/Filter ((?P<single>/[a-zA-Z0-9]*)|(?P<multiple>\[(.*?)\]))",
            header)
        if encode_method_matched != None:
            if encode_method_matched.group("single"):
                metadata['filter'] = [encode_method_matched.group('single')]
            else:
                metadata['filter'] = [
                    m.strip() for m in encode_method_matched.group(
                        "multiple").split(b' ') if m.strip() != b''
                ]
        stream_matched = re.match(
            r"(?P<stream>.*)\r?\nendstream".encode(),
            stream,
            re.DOTALL,
        )

        # if stream_matched is None:
        #     print(stream)
        stream = stream_matched.group("stream")
        decoded = None
        if b'/FlateDecode' in metadata.get(b"Filter", b""):
            decoded = zlib.decompress(stream)
        else:
            decoded = stream
        return {
            "metadata": metadata,
            "stream": decoded,
        }

    @property
    def obj_matcher(self):
        matchers = [
            r"^\<{2}((.|\r\n|\n)*)\>{2}$",  # dict matcher [index 0]
            # r"^\<{1}(?P<hexstr>(.|\r?\n)*)\>{1}$",  # hexdecimal string matcher
            # r"^\((?P<str>(.|\r?\n)*)\)$",  # string matcher
            # r"^\[(?P<array>(.|\r?\n)*)\]$",  # array matcher
            r"^stream((.|\r\n|\n)*)endstream$",  # stream matcher
        ]

        return "|".join(matchers).encode()


if __name__ == '__main__':
    with open(sys.argv[1], 'rb') as f:
        fc = f.read()

        PdfMutatur(fc)
