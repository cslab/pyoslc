from authlib.oauth1.rfc5849.errors import OAuth1Error
from flask import Blueprint, request, render_template, g, session, jsonify
from werkzeug.local import LocalProxy
from werkzeug.security import gen_salt

from oauth.models import User
from oauth.resources import OSLCOAuthConsumer, OAuthConfiguration
from oauth.server import server

oauth_bp = Blueprint('oauth', __name__, template_folder='templates')


def logout():
    if 'sid' in session:
        del session['sid']


def get_current_user():
    user = getattr(g, 'current_user', None)
    if user:
        return user
    sid = session.get('sid')
    if not sid:
        return None
    user = User.query.get(sid)
    if not user:
        logout()
        return None
    g.current_user = user
    return user


current_user = LocalProxy(get_current_user)


@oauth_bp.route('/initiate', methods=['POST'])
def initiate_temporary_credential():
    data = request.get_json(force=True)

    consumer_key = gen_salt(32)
    consumer_secret = data['secret'].encode('utf-8')
    consumer_name = data['name'].encode('utf-8')
    consumer_trusted = data['trusted']

    consumer = OSLCOAuthConsumer(consumer_key=consumer_key, consumer_secret=consumer_secret)
    consumer.name = consumer_name
    consumer.provisional = True
    consumer.trusted = consumer_trusted

    oauth_config = OAuthConfiguration.instance()
    oauth_config.add_consumer(consumer)

    # service = oauth_client.create_client('own')
    # callback_uri = url_for('.authorized', name=name, _external=True)
    # binded = service.authorize_redirect(callback_uri)
    # tempo = server.create_temporary_credentials_response()

    rsp = {'key': consumer_key}

    return jsonify(rsp)


@oauth_bp.route('/approveKey', methods=['GET', 'POST'])
def approve_key():
    if not request.args.has_key('key'):
        print('show admin')

    # request.headers.add('applicationName', 'PyOSLC')

    return render_template('oauth/admin_login.html', app_name='PyOSLC')


@oauth_bp.route('/authorize', methods=['GET', 'POST'])
def authorize():
    # make sure that user is logged in for yourself
    if request.method == 'GET':
        try:
            req = server.check_authorization_request()
            return render_template('authorize.html', req=req)
        except OAuth1Error as error:
            return render_template('error.html', error=error)

    granted = request.form.get('granted')
    if granted:
        grant_user = current_user
    else:
        grant_user = None

    try:
        return server.create_authorization_response(grant_user=grant_user)
    except OAuth1Error as error:
        return render_template('error.html', error=error)


@oauth_bp.route('/token', methods=['POST'])
def issue_token():
    return server.create_token_response()
