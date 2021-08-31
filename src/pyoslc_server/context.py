import sys

from werkzeug.exceptions import HTTPException

from pyoslc_server.wrappers import Request

from .globals import _request_ctx_stack

_sentinel = object()


class Context(object):

    def __init__(self, app, environ, request=None, session=None):
        self.app = app
        self.request = request if request else Request(environ)
        self.adapter = None

        try:
            self.adapter = app.get_adapter(self.request)
        except HTTPException as e:
            self.request.routing_exception = e

        self.preserved = False

    def match_request(self):
        try:
            result = self.adapter.match(return_rule=True)
            self.request.url_rule, self.request.view_args = result
        except HTTPException as e:
            self.request.routing_exception = e

    def push(self):
        top = _request_ctx_stack.top
        if top is not None:
            top.pop()

        if hasattr(sys, "exc_clear"):
            sys.exc_clear()

        _request_ctx_stack.push(self)

        if self.adapter is not None:
            self.match_request()

    def pop(self):
        res = _request_ctx_stack.pop()

        # get rid of circular dependencies at the end of the request
        # so that we don't require the GC to be active.
        res.request.environ["werkzeug.request"] = None

        assert res is self, "Popped wrong request context. (%r instead of %r)" % (
            res,
            self,
        )
