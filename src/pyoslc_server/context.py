from werkzeug.exceptions import HTTPException

from pyoslc_server.wrappers import Request


class Context:

    def __init__(self, app, environ, request=None, session=None):
        self.app = app
        self.request = request if request else Request(environ)
        self.adapter = app.get_adapter(self.request)
        self.session = session
        self.preserved = False
        self._preserved_exc = None

        self.match_request()

    def match_request(self):
        try:
            url_rule, self.request.view_args = self.adapter.match(return_rule=True)
            self.request.url_rule = url_rule
        except HTTPException as e:
            self.request.routing_exception = e
