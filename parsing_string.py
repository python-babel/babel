import re
import time

from cgi import parse_header
from collections import OrderedDict
@@ -44,9 +43,7 @@
def _parse_datetime_header(value):
    match = re.match(r'^(?P<datetime>.*?)(?P<tzoffset>[+-]\d{4})?$', value)

    tt = time.strptime(match.group('datetime'), '%Y-%m-%d %H:%M')
    ts = time.mktime(tt)
    dt = datetime.fromtimestamp(ts)
    dt = datetime.strptime(match.group('datetime'), '%Y-%m-%d %H:%M')

    # Separate the offset into a sign component, hours, and # minutes
    tzoffset = match.group('tzoffset')
