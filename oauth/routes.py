from authlib.oauth1.rfc5849.errors import OAuth1Error
from flask import Blueprint, request, render_template, jsonify, current_app
from flask_login import current_user

from oauth.models import Client, User
from oauth.server import auth_server
from oauth.forms import LoginConfirmForm, ConfirmForm
from webservice.api import login

oauth_bp = Blueprint('oauth', __name__, template_folder='templates')


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@oauth_bp.route('/', methods=['GET'])
def index():
    return "Hello"


@oauth_bp.route('/initiate', methods=['POST'])
def initiate_temporary_credential():
    current_app.logger.debug('Creating temporary credentials for the consumer')
    return auth_server.create_temporary_credentials_response()


@oauth_bp.route('/authorize', methods=['GET', 'POST'])
def authorize():
    if current_user.is_authenticated:
        form = ConfirmForm()
    else:
        form = LoginConfirmForm()

    if form.validate_on_submit():
        if form.confirm.data:
            grant_user = current_user
        else:
            # username = form.username.data.lower()
            # user = User.query.filter_by(username=username).first()
            # login_user(user)
            # grant_user = user
            # g.current_user = user

            grant_user = current_user
        return auth_server.create_authorization_response(request, grant_user)

    try:
        grant = auth_server.check_authorization_request()
    except OAuth1Error as error:
        # TODO: add an error page
        payload = dict(error.get_body())
        # return render_template('error.html', error=error)
        return jsonify(payload), error.status_code

    credential = grant.credential
    client_id = credential.get_client_id()
    client = Client.query.filter_by(client_id=client_id).first()
    return render_template(
        'oauth/authorize.html',
        grant=grant,
        client=client,
        form=form,
    )


@oauth_bp.route('/token', methods=['POST'])
def issue_token():
    return auth_server.create_token_response()
