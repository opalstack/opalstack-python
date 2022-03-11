import os
import string
import random
import textwrap

# Export pprint to tests
from pprint import pprint
pprint = pprint

# Short random identifier for uniqueness
RANDID = ''.join(random.choices(string.ascii_lowercase, k=4))

MYDIR = os.path.dirname(os.path.realpath(__file__))

def read_file(fpath):
    try:
        with open(fpath) as fp:
            return fp.read().strip()
    except FileNotFoundError: return None

APIKEY = read_file(os.path.join(MYDIR, 'apikey.txt'))
if not APIKEY:
    raise RuntimeError(textwrap.dedent('''
    Missing API Key.
        You must place a test account API key into tests/apikey.txt
        Important: Data will be deleted; use a separate test account for this.
    ''').strip())
