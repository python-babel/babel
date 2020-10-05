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
    if tzoffset is not None:
        plus_minus_s, rest = tzoffset[0], tzoffset[1:]
        hours_offset_s, mins_offset_s = rest[:2], rest[2:]
        # Make them all integers
        plus_minus = int(plus_minus_s + '1')
        hours_offset = int(hours_offset_s)
        mins_offset = int(mins_offset_s)
        # Calculate net offset
        net_mins_offset = hours_offset * 60
        net_mins_offset += mins_offset
        net_mins_offset *= plus_minus
        # Create an offset object
        tzoffset = FixedOffsetTimezone(net_mins_offset)
        # Store the offset in a datetime object
        dt = dt.replace(tzinfo=tzoffset)
