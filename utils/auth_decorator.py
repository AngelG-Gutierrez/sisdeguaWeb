from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Por favor inicia sesión para acceder a esta página')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function 