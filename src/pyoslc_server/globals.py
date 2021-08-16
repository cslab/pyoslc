from functools import partial

from werkzeug.local import LocalProxy
from werkzeug.local import LocalStack

def _lookup_req_object(name):
    top = _request_ctx_stack.top
    if top is None:
        raise RuntimeError(_request_ctx_err_msg)
    return getattr(top, name)

_request_ctx_stack = LocalStack()
request = LocalProxy(partial(_lookup_req_object, "request"))
session = LocalProxy(partial(_lookup_req_object, "session"))