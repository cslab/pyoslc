import logging

from flask import Blueprint, request
from flask_restx import Api
from werkzeug.exceptions import BadRequest

bp = Blueprint('oslc', __name__, url_prefix='/services')

api = Api(
    app=bp,
    version='1.0.0',
    title='Python OSLC API',
    description='Implementation for the OSLC specification for python application',
    default_mediatype='application/rdf+xml',
    contact='Contact Software & Koneksys',
    contact_url='https://www.contact-software.com/en/',
    contact_email="mario.carrasco@koneksys.com"
)


@bp.app_errorhandler(500)
def internal_error(error):
    logger = logging.getLogger('flask.app')
    logger.debug('Requesting INTERNAL_ERROR from: {}'.format(request.base_url))


@bp.before_request
def before_request_func():
    logger = logging.getLogger('flask.app')
    logger.debug('Requesting BEFORE_REQUEST from: {} to {}'.format(request.user_agent, request.base_url))
    logger.debug('Request Referrer {}'.format(request.referrer))


@api.errorhandler(BadRequest)
def handle_root_exception(error):
    """
    Return a custom message and 400 status code
    for bad requests from the html section
    """
    return {'message': error}, 400


@api.errorhandler
def default_error_handler(e):
    # if not settings.FLASK_DEBUG:
    return {'message': e}, 500
