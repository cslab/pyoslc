import six

if six.PY3:
    from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode, unquote
else:
    from urllib import urlencode, unquote
    from urlparse import urlparse, parse_qsl, urlunparse

from .http import HTTPStatus


def unpack(response, default_code=HTTPStatus.OK):
    if not isinstance(response, tuple):
        # data only
        return response, default_code, {}
    elif len(response) == 1:
        # data only as tuple
        return response[0], default_code, {}
    elif len(response) == 2:
        # data and code
        data, code = response
        return data, code, {}
    elif len(response) == 3:
        # data, code and headers
        data, code, headers = response
        return data, code or default_code, headers
    else:
        raise ValueError("Too many response values")


def get_url(url, params):
    new_url = urlparse(unquote(url))
    query = dict(parse_qsl(new_url.query.replace("&amp;", "&")))
    if params:
        query.update(params)
    query_string = urlencode(query)
    new_url = new_url._replace(query=query_string)
    return urlunparse(new_url)
