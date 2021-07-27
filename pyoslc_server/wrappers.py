from werkzeug import Request as RequestBase, Response as ResponseBase


class RDFMixing:

    @property
    def is_rdf(self):
        mt = self.mimetype
        return (
            mt == 'application/rdf+xml'
            or (mt.startswith('application/')) and mt.endswith('+xml')
        )

    @property
    def rdf(self):
        return self.get_rdf()

    def get_rdf(self):
        pass


class Request(RequestBase, RDFMixing):
    url_rule = None
    view_args = None
    routing_exception = None


class Response(ResponseBase, RDFMixing):
    default_mimetype = 'application/rdf+xml'
