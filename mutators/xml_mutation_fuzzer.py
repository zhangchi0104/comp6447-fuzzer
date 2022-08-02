from copy import deepcopy
import xml.etree.ElementTree as ET
from .mutator_base import MutatorBase


def retrieve(root, result):
    for _ in root:
        result.append(_)
        retrieve(_, result)
    return result


class XMLMutationFuzzer(MutatorBase):

    def __init__(self, seed):
        """
      args:
          seed: the seed csv bytes to mutate from
      """
        super().__init__()
        self._content = seed.decode()

    def _mutate_fuzz_url(self):
        root = ET.fromstring(self._content)

        tagList = retrieve(root, [])
        linklist = []

        for i in tagList:
            try:
                if (i.attrib['href']):
                    linklist.append(i)
            except:
                pass
        for i in linklist:
            i.set('href', "%s" * 100)

        xmlstr = ET.tostring(root)
        return xmlstr

    def _mutate_overflow(self):
        for num in range(32000, 60000, 2000):
            wideXML = "{}{}".format("<tag>" * num, "</tag>" * num)
        mutatedInput = bytearray(wideXML, 'UTF-8')
        return mutatedInput

    def format_output(self, raw):
        # construct the csv file body
        return raw
