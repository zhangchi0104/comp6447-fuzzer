import json
import re
from unittest import case
import file_code
from collections import OrderedDict
import xml.dom.minidom as dom
from xml.parsers.expat import ExpatError


def csv_matcher(sample_raw: bytes):
    sample = sample_raw.strip()
    lines = sample.split(b'\n')
    if len(lines) == 1:
        return False
    header = lines[0]
    col_headers = header.split(b',')
    if len(col_headers) < 2:
        return False
    cols = lines[1].split(b',')
    if len(cols) != len(col_headers):
        return False
    return True


def json_matcher(sample_raw: bytes):
    sample = sample_raw.strip()
    is_json_list = sample.startswith(b'{') and sample.endswith(b'}')
    is_json_obj = sample.startswith(b'[') and sample.endswith(b']')
    return is_json_list or is_json_obj


def xml_matcher(sample: bytes):
    try:
        dom.parseString(sample)
        return True
    except ExpatError:
        return False


def jepg_matcher(sample: bytes):
    SOI = b'\xff\xd8'
    EOI = b'\xff\xd9'
    return sample.startswith(SOI) and sample.endswith(EOI)


def elf_matcher(sample: bytes):
    MAGIC_NUMBER = 0x7f454c46
    return sample.startswith(MAGIC_NUMBER.to_bytes(4, 'little')) \
                or sample.startswith(MAGIC_NUMBER.to_bytes(4, 'big'))


def pdf_matcher(sample_raw: bytes):
    sample = sample_raw.strip()
    MATCHER_PATTERN = r"^\%PDF\-([1-9])\.([1-9]).*\%\%EOF$".encode()
    matches = re.match(MATCHER_PATTERN, sample, re.MULTILINE | re.DOTALL)
    return matches is not None


MATCHERS = {
    "jpeg": jepg_matcher,
    "elf": elf_matcher,
    "pdf": pdf_matcher,
    "csv": csv_matcher,
    "json": json_matcher,
    "xml": xml_matcher,
}


def infer_type(sample):
    for filetype, matcher in MATCHERS.items():
        if matcher(sample):
            return filetype
    return 'plaintext'


if __name__ == "__main__":
    import glob
    files = glob.glob('./tests/*')
    for file in files:
        with open(file, 'rb') as f:
            content = f.read()
            ft = infer_type(content)
            print(f"{file} -> {ft}")
