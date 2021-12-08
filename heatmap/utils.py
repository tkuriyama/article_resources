"""Utiltiy functions.
"""


import csv # type: ignore
import datetime as dt # type: ignore
from dataclasses import dataclass # type: ignore
from enum import Enum # type: ignore
import logging, log_setup # type: ignore
import re # type: ignore
import requests # type: ignore
from typing import Dict, List, Optional, TypedDict, TypeVar, Union # type: ignore


################################################################################
# Initialize Logging -- set logging level to > 50 to suppress all output

logger = log_setup.init_stream_log(__name__, logging.INFO)


################################################################################
# Status Types


@dataclass(frozen=True)
class OK:
    msg: str = 'OK'

@dataclass(frozen=True)
class Error:
    msg: str

Status = Union[OK, Error]


################################################################################
# Auth Types

class AuthDict(TypedDict):
    user: str
    pwd: str

MaybeAuth = Optional[AuthDict]


################################################################################
# HTTP


def http_get(url: str, auth: MaybeAuth = None) -> requests.Response:
    """Wrapper for requests.get().
    Excluding URL from logger text here as it may include API keys.
    """
    if auth:
        r = requests.get(url, auth=(auth['user'], auth['pwd']))
    else:
        r = requests.get(url)
    if r.status_code != 200:
        logger.warning(f'HTTP request returned code {r.status_code}')

    return r


################################################################################
# CSV


T = TypeVar('T')
Matrix = List[List[T]]


def csv_to_matrix(lines: List[str],
                  delim: str = ',',
                  quoted: bool = False,
                  quote: str = '"'
                  ) -> Matrix[str]:
    """Use the csv module reader to parse to list of lists."""
    return [line for line in
            csv.reader(lines,
                       quotechar=quote,
                       delimiter=delim,
                       quoting=(csv.QUOTE_ALL if quoted else csv.QUOTE_NONE),
                       skipinitialspace=True)]



################################################################################
# Numbers


class NumberStyle(Enum):
    US = 0
    EU = 1


def str_to_float(n: str, style: NumberStyle = NumberStyle.US) -> float:
    """Parse string to float."""
    if style == NumberStyle.US:
        n = n.replace(',', '')
    elif style == NumberStyle.EU:
        n = n.replace('.', '')
        n = n.replace(',', '.')

    for c in ('\'', '"', ':', ';'):
        n = n.replace(c, '')

    return float(n.strip())


def str_to_int(n: str, style: NumberStyle = NumberStyle.US) -> int:
    """Parse string to integer."""
    return int(str_to_float(n, style))


################################################################################
# Dates

def parse_date_name(date: str) -> Optional[dt.date]:
    """Parse date where month is a name."""
    p1 = r'([0-9]{1,2})[\s,/]+([a-z]+)[\s,/]+([0-9]{4})'
    p2 = r'([a-z]+)[\s,/]+([0-9]+)[\s,/]+([0-9]+)'
    p3 = r'([0-9]{4})[\s,/]+([a-z]+)[\s,/]+([0-9]{1,2})'

    mp1 = re.findall(p1, date, re.IGNORECASE)
    mp2 = re.findall(p2, date, re.IGNORECASE)
    mp3 = re.findall(p3, date, re.IGNORECASE)

    if mp1 and len(mp1[0]) == 3:
        d, m, y = mp1[0]
    elif mp2 and len(mp2[0]) == 3:
        m, d, y = mp2[0]
    elif mp3 and len(mp3[0]) == 3:
        y, m, d = mp3[0]
    else:
        y, m, d = 0, None, 0

    return maybe_date(int(y), month_to_int(m) if m else None, int(d))

def maybe_date(my: Optional[int],
               mm: Optional[int],
               md: Optional[int]
               ) -> Optional[dt.date]:
    """Return a date if int args for year, month, date are valid."""
    return (dt.date(my, mm, md) if my and my in range(0, 3000) and
                                   mm and mm in range(1, 13) and
                                   md and md in range(1, 32) else
            None)


def month_to_int(month: str) -> Optional[int]:
    """Attempt to parse month from word to int."""
    m = month.lower().strip()
    return (1 if m in ('jan', 'january') else
            2 if m in ('feb', 'february') else
            3 if m in ('mar', 'march') else
            4 if m in ('apr', 'april') else
            5 if m in ('may',) else
            6 if m in ('jun', 'june') else
            7 if m in ('jul', 'july') else
            8 if m in ('aug', 'august') else
            9 if m in ('sep', 'sept', 'september') else
            10 if m in ('oct', 'october') else
            11 if m in ('nov', 'november') else
            12 if m in ('dec', 'december') else
            None)


################################################################################
# Helpers


def url_join(paths: List[str], params: Optional[Dict[str, str]] = None) -> str:
    """Construct URL with REST syntax."""
    url = ''

    # ensure joins with '/' but ignore final '/'
    for path in paths:
        url += path if path[-1] == '/' else '{}/'.format(path)
    url_ = url[:-1]

    if params:
        url_ += '?' + '&'.join('{}={}'.format(k, v)
                               for k, v in params.items())
    return url_
