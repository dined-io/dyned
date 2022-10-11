#!/usr/bin/env python
"""
This module is a client that allows the user to interact with the dined API
This should be a swagger client in the future
"""
import json
import requests
from requests.exceptions import HTTPError
from dined.config import BASE_URL
# import hashlib

def raw_issue_request(method, url, data=None, binary=False):
    """
    Issues a request to the dined API
    """

    if data is not None and not binary:
        data = json.dumps(data)
    response = requests.request(method, url, data=data)
    try:
        response.raise_for_status()
        try:
            data = response
        except ValueError:
            data = response
    except HTTPError as error:
        print(f"Caught an HTTPError: {error}")
        print("Body:\n", response.content)
        raise
    return data


def issue_request(method, endpoint, *args, **kwargs):
    """
    Issues a specific request to the dined API
    """
    return raw_issue_request(
        method, BASE_URL.format(endpoint=endpoint), *args, **kwargs
    )
