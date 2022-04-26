import sys

from six import reraise
from werkzeug.exceptions import HTTPException

from pyoslc_server.wrappers import Request

from .globals import _request_ctx_stack, _app_ctx_stack

_sentinel = object()


class AppContext(object):
    def __init__(self, app):
        self.app = app
        self.adapter = app.get_adapter(None)
        self._refcnt = 0

    def push(self):
        """Binds the app context to the current context."""
        self._refcnt += 1
        if hasattr(sys, "exc_clear"):
            sys.exc_clear()
        _app_ctx_stack.push(self)
        # appcontext_pushed.send(self.app)

    def pop(self, exc=_sentinel):
        """Pops the app context."""
        try:
            self._refcnt -= 1
            if self._refcnt <= 0:
                if exc is _sentinel:
                    exc = sys.exc_info()[1]
                self.app.do_teardown_appcontext(exc)
        finally:
            rv = _app_ctx_stack.pop()
        assert rv is self, "Popped wrong app context.  (%r instead of %r)" % (rv, self)
        # appcontext_popped.send(self.app)

    def __enter__(self):
        self.push()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.pop(exc_value)

        if False and exc_type is not None:
            reraise(exc_type, exc_value, tb)


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
