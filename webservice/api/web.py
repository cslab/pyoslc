from flask import Blueprint, render_template

bp = Blueprint('web', __name__)


@bp.route('/')
def index():
    return render_template('web/index.html')


