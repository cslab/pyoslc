from app.api.adapter import bp, api
from app.api.adapter.dialogs.routes import dialog_bp
from app.api.adapter.namespaces.config.routes import config_ns
from app.api.adapter.namespaces.core import adapter_ns
from app.api.adapter.namespaces.rm import rm_ns


def init_app(app):
    app.register_blueprint(bp, url_prefix='/oslc')
    api.add_namespace(adapter_ns)
    api.add_namespace(rm_ns)
    # api.add_namespace(config_ns)
    app.register_blueprint(dialog_bp, url_prefix='/oslc/services')


