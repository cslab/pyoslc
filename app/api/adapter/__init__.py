import logging

from flask import Blueprint, request
from flask_restx import Api

bp = Blueprint("oslc", __name__, url_prefix="/services", static_folder="static")

api = Api(
    app=bp,
    version="1.0.0",
    title="Python OSLC API",
    description="Implementation for the OSLC specification for python application",
    contact="Contact Software & Koneksys",
    contact_url="https://www.contact-software.com/en/",
    contact_email="mario.carrasco@koneksys.com",
    validate=True,
)


@bp.app_errorhandler(500)
def internal_error(error):
    logger = logging.getLogger("flask.app")
    logger.debug("Requesting INTERNAL_ERROR from: {}".format(request.base_url))


@bp.before_request
def before_request_func():
    logger = logging.getLogger("flask.app")
    logger.debug(
        "Requesting from: {} {} to {}".format(
            request.access_route, request.user_agent, request.base_url
        )
    )
    # logger.debug('Request Referrer {}'.format(request.referrer))


@api.errorhandler
def default_error_handler(e):
    # if not settings.FLASK_DEBUG:
    return {"message": e}, 500
