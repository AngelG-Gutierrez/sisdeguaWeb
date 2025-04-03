from flask import Blueprint, render_template

pages_db = Blueprint('pages', __name__)

@pages_db.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@pages_db.route('/reportes')
def reportes():
    return render_template('reportes.html') 