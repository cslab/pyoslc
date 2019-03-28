from flask import Blueprint
from flask_restplus import Api

bp = Blueprint('oslc', __name__, '/oslc')

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


from webservice.api.oslc.rm import rm_ns
# from webservice.api.oslc.cm import cm_ns
