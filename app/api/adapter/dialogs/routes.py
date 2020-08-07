from flask import Blueprint, render_template, url_for, request

from app.api.adapter.forms import SpecificationForm, SelectSpecificationForm
from app.api.adapter.namespaces.business import get_requirement_list, get_requirements

dialog_bp = Blueprint('dialog', __name__, template_folder='templates')


@dialog_bp.route('/provider/<service_provider_id>/resources/selector', methods=['GET', 'POST'])
def index(service_provider_id):
    form = SelectSpecificationForm()
    list_req = None

    if form.validate_on_submit():
        base_url = 'http://localhost:5000/oslc/services/provider/Project-1/resources/selector'

        list_req = get_requirements()

    return render_template("dialogs/selector.html", form=form, list_req=list_req)


@dialog_bp.route('/provider/<service_provider_id>/resources/creator')
def create(service_provider_id):
    form = SpecificationForm()
    return render_template("dialogs/selector.html", form=form)