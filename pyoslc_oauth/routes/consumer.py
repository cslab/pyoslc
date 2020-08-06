from flask import Blueprint, current_app, request, url_for, jsonify, abort, render_template, redirect
from flask_login import login_required
from werkzeug.security import gen_salt

from pyoslc_oauth import OAuthConfiguration, OSLCOAuthConsumer
from pyoslc_oauth.database import db
from pyoslc_oauth.models import Client

consumer_bp = Blueprint('consumer', __name__)


@consumer_bp.route('/')
def get_consumers():
    current_app.logger.info('Listing the consumers')
    oauth_config = OAuthConfiguration.get_instance()
    oauth_app = oauth_config.application
    if not oauth_app.is_admin_session():
        return 405, 'You must be ad administrator'

    consumer_store = oauth_config.consumer_store
    consumers = consumer_store.consumer_values

    provisional = list()
    approved = list()
    for consumer in consumers:
        if consumer.provisional:
            provisional.append(consumer)
        else:
            approved.append(consumer)

    return {'provisional': provisional, 'approved': approved}


@consumer_bp.route('/register', methods=['POST'])
def register():
    current_app.logger.debug('Registering a new consumer')
    data = request.get_json(force=True)

    consumer_key = gen_salt(32)
    consumer_secret = data['secret'].encode('utf-8')
    consumer_name = data['name'].encode('utf-8')
    consumer_trusted = data['trusted']

    consumer = OSLCOAuthConsumer(consumer_key=consumer_key, consumer_secret=consumer_secret)
    consumer.name = consumer_name
    consumer.provisional = True
    consumer.trusted = bool(consumer_trusted)

    oauth_config = OAuthConfiguration.get_instance()
    oauth_config.consumer_store.add_consumer(consumer)

    callback_uri = url_for('oauth.authorize', _external=True)

    client = Client(
        name=consumer.name,
        client_id=consumer.key,
        client_secret=consumer.secret,
        default_redirect_uri=callback_uri,
    )
    db.session.add(client)
    db.session.commit()

    rsp = {'key': consumer_key}
    current_app.logger.debug('Consumer registered')

    return jsonify(rsp)


@consumer_bp.route('/approve', methods=['GET', 'POST'])
def approve():
    current_app.logger.debug('Requesting the approval for the consumer')
    if not request.args.get('key') and not request.json['key']:
        return show_consumer_key_management()

    consumer_key = request.args.get('key') or request.json['key']

    oauth_config = OAuthConfiguration.get_instance()

    consumer_store = oauth_config.consumer_store
    consumers = consumer_store.consumers
    consumer = consumers[consumer_key]

    callback_uri = url_for('oauth.authorize', _external=True)
    authorize_uri = url_for('oauth.initiate_temporary_credential', _external=True)
    access_token_url = url_for('oauth.issue_token', _external=True)

    consumer.init_app(current_app)
    consumer.register(
        name=consumer.name,
        client_id=consumer.key,
        client_secret=consumer.secret,
        request_token_url=authorize_uri,
        authorize_url=callback_uri,
        access_token_url=access_token_url,
    )
    client = consumer.create_client(consumer.name)

    redirect_uri = url_for('.authorized', key=consumer.key, _external=True)
    binded = client.authorize_redirect(redirect_uri)
    return binded


@consumer_bp.route('/approve/<key>', methods=['GET', 'POST'])
@login_required
def authorized(key):
    current_app.logger.debug('Authorizing the consumer')

    oauth_config = OAuthConfiguration.get_instance()
    consumer_store = oauth_config.consumer_store
    consumers = consumer_store.consumers
    consumer = consumers[key]

    if not consumer:
        return abort(404)

    consumer.provisional = False
    consumer_store.update_consumer(consumer)

    # client = Client.query.filter_by(client_id=consumer.key).first()

    return 'Consumer has been approved, click on finish button'


@consumer_bp.route('/admin', methods=['GET'])
def show_consumer_key_management():
    oauth_config = OAuthConfiguration.get_instance()
    oauth_app = oauth_config.application

    if not oauth_app.is_admin_session():
        return show_admin_login(oauth_app)

    consumers = get_consumers()

    return render_template('pyoslc_oauth/manage_consumer.html', consumers=consumers)


def show_admin_login(oauth_app, form=None):
    callback_url = request.base_url
    query = request.query_string
    if query:
        callback_url += '?'
        callback_url += query

    admin_login_url = url_for('oauth.admin_login')

    if not form:
        form = AdminLogin()
        form.action = admin_login_url
        form.callback.data = callback_url

    return render_template(
        'pyoslc_oauth/admin_login.html',
        app_name=oauth_app.name,
        form=form,
        admin_login_url=admin_login_url,
        callback_url=callback_url
    )


@consumer_bp.route('/adminLogin', methods=['POST'])
def admin_login():
    data = request.get_data()

    url = url_for('oauth.approve_key')

    return redirect(url)
