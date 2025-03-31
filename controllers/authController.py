from flask import Blueprint, Flask, render_template, request, redirect, url_for
import os
from database.queries import login_user, register_user

auth_db = Blueprint('auth', __name__)
app = Flask(__name__, template_folder=os.path.join('templates'))

@auth_db.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        response, error = login_user(email, password)
        
        if error:
            return render_template('./auth/login.html', error=error)
        
        return redirect(url_for('statistics.statistics'))
        
    return render_template('./auth/login.html')

@auth_db.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        response, error = register_user(email, password)
        
        if error:
            return render_template('./auth/register.html', error=error)
            
        return redirect(url_for('./auth/login.html'))
        
    return render_template('./auth/register.html')
