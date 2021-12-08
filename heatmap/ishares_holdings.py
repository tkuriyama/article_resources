"""Parse iShares holdings CSV.
"""

import datetime as dt # type: ignore
import logging, log_setup # type: ignore
import pandas as pd # type: ignore
from typing import List, Optional, Tuple, TypedDict # type : ignore
import re # type: ignore
import utils # type: ignore


################################################################################
# Initialize Logging -- set logging level to > 50 to suppress all output

logger = log_setup.init_stream_log(__name__, logging.INFO)


################################################################################

class FundRef(TypedDict):
    name: str
    holdings_date: dt.date
    inception: dt.date
    shares_outstanding: int


################################################################################
# HTTP

def get(url: str) -> Tuple[Optional[FundRef], pd.DataFrame]:
    """Get and parse iShares ETF holdings from url."""
    r = utils.http_get(url)
    lines = [line.strip() for line in r.text.split('\n') if line.strip()]

    if len(lines) < 9:
        logger.error(f'Too few lines in file from {url}')
        return None, pd.DataFrame()

    m = utils.csv_to_matrix(lines, ',', True)
    fund_ref = parse_fund_ref(m[:8])
    fund_holdings = parse_rows(m[8:]) if fund_ref else pd.DataFrame()
    return fund_ref, fund_holdings


################################################################################
# Parse Reference Data


def parse_fund_ref(m: utils.Matrix[str]) -> Optional[FundRef]:
    """Parse FundRef dict from lines."""
    name = parse_name(m[0])
    holdings = parse_date(m[1], 'fund holdings')
    inception = parse_date(m[2], 'inception')
    try:
        shrs = parse_int(m[3], 'shares outstanding')
    except Exception as e:
        logger.error(f'Could not parse shares outstanding: {e}')
        shrs = 0

    return (None if not (name and holdings and inception and shrs) else
            {'name': name,
             'holdings_date': holdings,
             'inception': inception,
             'shares_outstanding': shrs
             })


def parse_name(line: List[str]) -> Optional[str]:
    """Parse fund name"""
    if len(line) != 1:
        logger.error('Exactly one value expected in {}'.format(str(line)))
        return None

    xs = re.findall(r'\ufeff(.+)', line[0])
    if len(xs) != 1:
        name = None
        logger.error('Could not parse name {} with regex'.format(xs[0]))
    else:
        name = xs[0]
    return name


def parse_date(line: List[str], name: str) -> Optional[dt.date]:
    """Parse date."""
    if len(line) != 2:
        logger.error('Exactly two values expected in {}'.format(str(line)))
        return None
    elif name.lower() not in line[0].lower():
        logger.error('Expecting label {} in {}'.format(name, line[0]))
        return None

    return utils.parse_date_name(line[1])


def parse_int(line: List[str], name: str) -> Optional[int]:
    """Parse shares outstanding."""
    if len(line) != 2:
        logger.error('Exactly two values expected in {}'.format(str(line)))
        return None
    elif name.lower() not in line[0].lower():
        logger.error('Expecting label {} in {}'.format(name, line[0]))
        return None

    return utils.str_to_int(line[1])


################################################################################
# Parse Body


def parse_rows(m: utils.Matrix[str]) -> pd.DataFrame:
    """Parse rows to DataFrame, expecting specific columns and types."""
    if len(m) < 2:
        logger.error('More than one line expected in {}'.format(str(m)))
        return pd.DataFrame()

    # parse data rows and add type casting
    cols = len(m[0])
    df = pd.DataFrame([row for row in m[1:] if len(row) == cols],
                      columns=m[0])

    pairs = (('Market Value', utils.str_to_float),
             ('Weight (%)', utils.str_to_float),
             ('Notional Value', utils.str_to_float),
             ('Shares', utils.str_to_int),
             ('Price', utils.str_to_float),
             ('FX Rate', utils.str_to_float),
             ('Accrual Date', utils.parse_date_name)
             )

    for col, f in pairs:
        try:
            df[col] = df[col].apply(f)
        except Exception as e:
            logger.error('Error when casting {}: {}'.format(col, e))

    return df
