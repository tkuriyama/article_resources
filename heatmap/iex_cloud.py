"""IEX Cloud API.
Implements convenience functions for calling the API with requests.

https://iexcloud.io/docs/api/#api-reference
https://intercom.help/iexcloud/en/articles/2851957-how-to-use-the-iex-cloud-api
"""

import requests # type: ignore
from typing import Dict # type: ignore
import utils # type: ignore


################################################################################
# Rest API


PROD = 'https://cloud.iexapis.com/'
SBOX = 'https://sandbox.iexapis.com/'
VER = 'stable/'


def get(endpoint: str,
        query_params: Dict[str, str],
        api_token: str,
        base: str = PROD,
        version: str = VER
        ) -> requests.Response:
    """Single GET call."""
    query_params['token'] = api_token
    url = utils.url_join([base, version, endpoint], query_params)
    return utils.http_get(url)


################################################################################
# Convenience Functions


def previous(api_token: str, ticker: str) -> requests.Response:
    """Previous endpoint."""
    return get(f'stock/{ticker}/previous', {}, api_token)

