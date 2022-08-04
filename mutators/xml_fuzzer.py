from types import new_class
import xml.etree.ElementTree as ET
import random
if __name__ == '__main__':
    from mutator_base import MutatorBase
else:
    from mutators import MutatorBase


class XMLMutator(MutatorBase):

    def __init__(self, seed):
        super().__init__()
        self._content = ET.ElementTree(ET.fromstring(seed))
        self._seed = seed

    def format_output(self, data):
        if data:
            return data
        res = ET.tostring(self._content.getroot(), method='xml')
        self._content = ET.ElementTree(ET.fromstring(self._seed))
        return res

    def _mutate_make_longer_tag(self):

        def _alter_tag(node: ET.Element):
            node.tag = self.pick_from_alphabet(0xff)

        self._recusive_apply(self.root, _alter_tag)

    def _recusive_apply(self, node: ET.Element, fn):
        children = list(node)
        fn(node)
        for child in children:
            self._recusive_apply(child, fn)

    def _mutate_forge_attributes(self):
        # append children
        for _ in range(0xff):
            # any luck with format string?
            el = ET.Element("h1", {"id": "%s" * 10})
            self.root.append(el)

    def _mutate_recursion_overflow(self):
        # Python breaks when using ET.ElementTree to parse
        # Have to do it with raw string
        return b'<fuz>' * 0xffff + b'</fuz>' * 0xffff

    def _mutate_alter_href(self):

        def alter_href(node: ET.Element):
            node.set("href", "%s" * 10)

        self._recusive_apply(self.root, alter_href)

    @property
    def root(self):
        return self._content.getroot()

    def pick_from_alphabet(self, length):
        ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
        res = ""
        for _ in range(length):
            i = random.randint(0, 25)
            res += ALPHABET[i]
        return res


if __name__ == '__main__':
    with open('tests/xml2.txt', 'rb') as f:
        m = XMLMutator(f.read())
