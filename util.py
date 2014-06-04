import calendar
import time

import dateutil.parser

def parse_8601(s):
    return calendar.timegm(dateutil.parser.parse(s).timetuple())

def hours_ago(tstamp):
    if isinstance(tstamp, basestring):
        tstamp = parse_8601(tstamp)
    return (time.time() - tstamp) / 3600
