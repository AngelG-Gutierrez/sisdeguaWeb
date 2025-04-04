from flask import Blueprint, Flask, render_template, request, redirect, url_for, session
import os
from database.supaBase import login_user, register_user
from flask import make_response

auth_db = Blueprint('auth', __name__)
app = Flask(__name__, template_folder=os.path.join('templates'))

@auth_db.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:  # Si ya está logueado, redirigir a statistics
        return redirect(url_for('statistics.statistics'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        response, error = login_user(email, password)
        
        if error:
            return render_template('./auth/login.html', error=error)
        
        session['logged_in'] = True
        session['user_email'] = email
        
        return redirect(url_for('statistics.statistics'))
    
    response = make_response(render_template('./auth/login.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@auth_db.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_db.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        response, error = register_user(email, password)
        
        if error:
            return render_template('./auth/register.html', error=error)
            
        return redirect(url_for('auth.login'))
        
    return render_template('./auth/register.html')
