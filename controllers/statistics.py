import os
from flask import Blueprint, Flask, render_template
from utils.auth_decorator import login_required

statistics_db = Blueprint('statistics', __name__)
app = Flask(__name__, template_folder=os.path.join('templates')) 

@statistics_db.route('/statistics', methods=['GET', 'POST'])
@login_required
def statistics():
    return render_template('estadisticas.html')