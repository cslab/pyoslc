from flask import make_response
from simplexml import dumps


def output_xml(data, code, headers=None):
    """Makes a Flask response with a XML encoded body"""
    resp = make_response(dumps({'response': data}), code)
    resp.headers.extend(headers or {})
    return resp


def outpu_rdf_xml(data, code, headers=None):
    resp = make_response(dumps({'response': data}), code)
    resp = make_response(dumps({'response': data}), code)
    resp.headers.extend(headers or {})
    return resp
