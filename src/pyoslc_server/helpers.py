import re

from .globals import _request_ctx_stack
from .wrappers import Response

FIRST_CAP_RE = re.compile("(.)([A-Z][a-z]+)")
ALL_CAP_RE = re.compile("([a-z0-9])([A-Z])")


def camel_to_dash(value):
    """
    Transform a CamelCase string into a low_dashed one

    :param str value: a CamelCase string to transform
    :return: the low_dashed string
    :rtype: str
    """
    first_cap = FIRST_CAP_RE.sub(r"\1_\2", value)
    return ALL_CAP_RE.sub(r"\1_\2", first_cap).lower()


def url_for(endpoint, **values):
    reqctx = _request_ctx_stack.top

    # If request specific information is available we have some extra
    # features that support "relative" URLs.
    if reqctx is not None:
        adapter = reqctx.adapter

        if endpoint[:1] == ".":
            if blueprint_name is not None:
                endpoint = blueprint_name + endpoint
            else:
                endpoint = endpoint[1:]

        external = values.pop("_external", False)

    # Otherwise go with the url adapter from the appctx and make
    # the URLs external by default.
    else:
        adapter = appctx.adapter

        if adapter is None:
            raise RuntimeError(
                "Application was not able to create a URL adapter for request"
                " independent URL generation. You might be able to fix this by"
                " setting the SERVER_NAME config variable."
            )

        external = values.pop("_external", True)

    anchor = values.pop("_anchor", None)
    method = values.pop("_method", None)
    scheme = values.pop("_scheme", None)
    # appctx.app.inject_url_defaults(endpoint, values)

    # This is not the best way to deal with this but currently the
    # underlying Werkzeug router does not support overriding the scheme on
    # a per build call basis.
    old_scheme = None
    if scheme is not None:
        if not external:
            raise ValueError("When specifying _scheme, _external must be True")
        old_scheme = adapter.url_scheme
        adapter.url_scheme = scheme

    try:
        try:
            rv = adapter.build(
                endpoint, values, method=method, force_external=external
            )
        finally:
            if old_scheme is not None:
                adapter.url_scheme = old_scheme
    except BuildError as error:
        # We need to inject the values again so that the app callback can
        # deal with that sort of stuff.
        values["_external"] = external
        values["_anchor"] = anchor
        values["_method"] = method
        values["_scheme"] = scheme
        return appctx.app.handle_url_build_error(error, endpoint, values)

    if anchor is not None:
        rv += "#" + url_quote(anchor)
    return rv


def make_response(*args):
    if not args:
        return Response()
    if len(args) == 1:
        args = args[0]
    return current_app.make_response(args)
