from base64 import b64decode, b64encode
from binascii import Error as BinAsciiError

from .exceptions import ViewStateException

CONSTS = {
    100: {},
    101: '',
    102: 0,
    103: True,
    104: False
}

def parse_const(b):
    return CONSTS.get(b, None)

def parse_string(b):
    n = b[0]
    s = b[1:n+1]
    return s.decode(), b[n+1:]

def parse_pair(b):
    first, remain = _parse(b)
    second, remain = _parse(remain)
    return (first, second), remain

def _parse(b):

    if not b:
        return None
    else:
        assert type(b) == bytes().__class__
        print(b)

    if 100 <= b[0] <= 104:
        return parse_const(b[0]), b[1:]
    elif b[0] == 0x5:
        return parse_string(b[1:])
    elif b[0] == 0xf:
        return parse_pair(b[1:])
    else:
        return b, bytes()

    return None

def parse(b):
    return _parse(b)[0]


class ViewState(object):

    def __init__(self, base64=''):
        self.base64 = base64
        self.decoded = None
        try:
            self.raw = b64decode(self.base64)
        except BinAsciiError as bae:
            raise ViewStateException('Cannot decode base64 input')

    @property
    def preamble(self):
        return self.raw[:2]

    @property
    def body(self):
        return self.raw[2:]

    def is_valid(self):
        format_marker = b'\xff'
        version_marker = b'\x01'
        preamble = format_marker + version_marker
        return self.preamble == preamble

    def decode(self):
        if not self.is_valid():
            raise ViewStateException('Cannot decode invalid viewstate, bad preamble')
        self.decoded = parse(self.body)
        return self.decoded