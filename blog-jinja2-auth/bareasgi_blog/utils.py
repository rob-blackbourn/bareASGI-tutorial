"""Utilities"""

from datetime import timedelta
import re
from typing import Optional

TIMEDELTA_REGEX = re.compile(
    r'^((?P<weeks>\d+?)w)?((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?$'
)

def parse_timedelta(text: str) -> Optional[timedelta]:
    """Parse a timedelta
    
    :param text: The text to parse
    :type text: str
    :return: The parsed timedelta
    :rtype: Optional[timedelta]
    """
    parts = TIMEDELTA_REGEX.match(text)
    if not parts:
        return None
    matches = parts.groupdict()
    time_params = {}
    for (name, param) in matches.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)
