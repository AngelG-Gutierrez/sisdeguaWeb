from flask import Flask, render_template
import os
from controllers.authController import auth_db

app = Flask(__name__, template_folder=os.path.join('views', 'templates'))

@app.route('/')
def index():
    return render_template('index.html')

app.register_blueprint(auth_db) 


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)