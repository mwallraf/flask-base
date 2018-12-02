from flask import (
    Blueprint,
    render_template
)


rtd = Blueprint('rtd', __name__, static_folder='docs')

@rtd.route('/')
def index():
    """Provisioning dashboard page."""
    return render_template('rtd/index.html')

