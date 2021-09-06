import werkzeug
from werkzeug.test import Client

from .globals import _request_ctx_stack


class OSLCAPPClient(Client):

    preserve_context = False

    def __init__(self, *args, **kwargs):
        super(OSLCAPPClient, self).__init__(*args, **kwargs)
        self.environ_base = {
            "REMOTE_ADDR": "127.0.0.1",
            "HTTP_USER_AGENT": "werkzeug/" + werkzeug.__version__,
        }

    def __enter__(self):
        if self.preserve_context:
            raise RuntimeError("Cannot nest client invocations")
        self.preserve_context = True
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.preserve_context = False

        # Normally the request context is preserved until the next
        # request in the same thread comes. When the client exits we
        # want to clean up earlier. Pop request contexts until the stack
        # is empty or a non-preserved one is found.
        while True:
            top = _request_ctx_stack.top

            if top is not None and top.preserved:
                top.pop()
            else:
                break
