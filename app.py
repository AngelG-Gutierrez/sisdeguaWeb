from flask import Flask, render_template
import os
from controllers.authController import auth_db
from controllers.statistics import statistics_db
from controllers.pagesController import pages_db
from controllers.reports import reports_db

app = Flask(__name__, template_folder=os.path.join('templates'))
app.secret_key = 'tu_clave_secreta_aqui'

@app.route('/')
def index():
    return render_template('index.html')

app.register_blueprint(auth_db) 
app.register_blueprint(statistics_db)
app.register_blueprint(pages_db)
app.register_blueprint(reports_db)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)