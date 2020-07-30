from flask import Blueprint

from pyoslc.vocabulary.rm import OSLC_RM

external_bp = Blueprint('external', __name__, template_folder='templates')


@external_bp.route('fields')
def mapping():
    fields = {
        'domain': OSLC_RM.uri,
        'artifact': OSLC_RM.Requirement,
        'attributes': {
            'Specification_id': {
                'oslc': 'identifier'
            },
            'Title': {
                'oslc': 'title'
            },
            'Description': {
                'oslc': 'description'
            },
            'Author': {
                'oslc': 'creator'
            },
            'Product': {
                'oslc': 'shortTitle',
                'py': 'short_title'
            },
            'Subject': {
                'oslc': 'subject',
                'py': 'subject'
            },



        }

    }

    return fields