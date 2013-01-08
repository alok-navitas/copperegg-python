import requests
import sys
import urllib2
from functools import wraps


def try_get_json(response):
    data = None
    try:
        if response:
            data = response.json()
    except ValueError, err:
        sys.stderr.write('CopperEgg JSON error: {}\n'.format(str(err)))
        data = None
    return data


def print_error(err, response):
    sys.stderr.write('CopperEgg HTTP error: {}\n'.format(str(err)))
    sys.stderr.write('-- response: {}\n'.format(response.text))


def handle_errors(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        response = None
        try:
            response = fn(*args, **kwargs)
            response.raise_for_status()
        except requests.HTTPError, err:
            print_error(err, response)
            response = None
        except urllib2.URLError, err:
            print_error(err, response)
            response = None
        return response
    return wrapped


def return_json(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        ignore_response = False
        if 'ignore_response' in kwargs:
            ignore_response = kwargs['ignore_response']
            del kwargs['ignore_response']

        response = fn(*args, **kwargs)

        if ignore_response:
            return None
        else:
            return try_get_json(response)
    return wrapped
