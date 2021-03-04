from flask import Blueprint, render_template, request, jsonify, make_response

from app.api.adapter.forms import SpecificationForm, SelectSpecificationForm
from app.api.adapter.namespaces.business import get_requirements, create_requirement

dialog_bp = Blueprint('dialog', __name__, template_folder='templates', static_folder='static')


@dialog_bp.route('/provider/<service_provider_id>/resources/selector', methods=['GET', 'POST'])
def index(service_provider_id):
    selection_url = request.base_url
    selection_type_url = selection_url.replace('selector', 'types')

    form = SelectSpecificationForm()
    list_req = None

    resource_type = request.args.get('type')
    if resource_type:
        requirements = get_requirements(selection_url)
        terms = request.args.get('terms', None)

        results = list()
        for r in requirements:
            if terms != '':
                if r.identifier.__contains__(terms) or r.title.__contains__(terms) or r.description.__contains__(terms):
                    results.append({
                        'oslc:label': r.identifier + ' / ' + r.title,
                        'rdf:resource': str(r.about)
                    })
            else:
                results.append({
                    'oslc:label': r.identifier + ' / ' + r.title,
                    'rdf:resource': str(r.about)
                })

        return jsonify({'oslc:results': results})

    return render_template("dialogs/selector.html", selection_url=selection_url,
                           selection_type_url=selection_type_url, form=form, list_req=list_req)


@dialog_bp.route('/provider/<service_provider_id>/resources/creator', methods=['GET', 'POST'])
def create(service_provider_id):
    creator_url = request.base_url
    form = SpecificationForm()

    if form.validate_on_submit():

        req = create_requirement(form.data)

        results = [{
            'rdf:resource': creator_url.replace('creator', 'requirement') + '/' + req.identifier,
            'oslc:label': req.identifier
        }]

        response = make_response(jsonify({"oslc:results": results}), 201)

        response.headers['Content-Type'] = 'application/rdf+xml; charset=UTF-8'
        response.headers['OSLC-Core-Version'] = "2.0"
        response.headers['Location'] = creator_url + '/' + req.identifier

        return response

    return render_template("dialogs/creator.html", creator_url=creator_url, form=form)


@dialog_bp.route('/provider/<service_provider_id>/resources/types', methods=['GET'])
def types(service_provider_id):
    results = list()
    results.append({
        'oslc:label': 'Specification',
        'rdf:resource': str('specification')
    })

    return jsonify({'oslc:results': results})
