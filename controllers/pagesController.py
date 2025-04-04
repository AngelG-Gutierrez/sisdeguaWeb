from flask import Blueprint, render_template
from utils.auth_decorator import login_required

pages_db = Blueprint('pages', __name__)

@pages_db.route('/nosotros')
@login_required
def nosotros():
    return render_template('nosotros.html')

@pages_db.route('/reportes')
@login_required
def reportes():
    return render_template('reportes.html') 