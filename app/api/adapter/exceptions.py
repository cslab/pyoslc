from werkzeug.exceptions import HTTPException


class NotModified(HTTPException):
    """*304* `Not Modified`

    Raise if the client sent a resource with no changes to be stored.
    """

    code = 304
    description = (
        "The client sent the same resource without changes to the server, "
        "it can not be updated."
    )
