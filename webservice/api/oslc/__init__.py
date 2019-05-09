import logging

from flask import Blueprint
from flask_restplus import Api
from werkzeug.exceptions import BadRequest

from webservice.api.oslc.adapter.endpoints import adapter_ns

log = logging.getLogger(__name__)

bp = Blueprint('oslc', __name__, static_folder='/oslc', url_prefix='services')

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


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(e)

    # if not settings.FLASK_DEBUG:
    return {'message': e}, 500


@api.errorhandler(BadRequest)
def handle_root_exception(error):
    """
    Return a custom message and 400 status code
    for bad requests from the html section
    """

    return {'message': 'What you want'}, 400


api.add_namespace(adapter_ns)

# from webservice.api.oslc.adapter import adapter_ns
from webservice.api.oslc.rm import rm_ns
# from webservice.api.oslc.cm import cm_ns
