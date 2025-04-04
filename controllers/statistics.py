import os
from flask import Blueprint, Flask, render_template
from utils.auth_decorator import login_required
from database.astraDB import AstraDB
from flask import jsonify
from datetime import datetime, timezone

statistics_db = Blueprint('statistics', __name__)
app = Flask(__name__, template_folder=os.path.join('templates')) 

@statistics_db.route('/statistics', methods=['GET', 'POST'])
@login_required
def statistics():
    astra = AstraDB()
    datos_actuales = astra.get_data_real()
    datos_historicos = astra.get_sensor_data()
    return render_template('estadisticas.html',
    datos_actuales=datos_actuales,
    datos_historicos=datos_historicos)

@statistics_db.route('/api/table', methods=['GET'])
@login_required
def obtener_datos_historicos():
    astra = AstraDB()
    datos_historicos = astra.get_sensor_data_limit()

    datos_filtrados = [
        {
            "fecha": datetime.fromtimestamp(registro.get("date").timestamp_ms / 1000, tz=timezone.utc).isoformat(),            
            "nivel_agua": registro.get("waterlevel"),
            "nivel_lluvia": registro.get("rainlevel")
        } 
        for registro in datos_historicos
    ]
    return jsonify(datos_filtrados)

@statistics_db.route('/api/datos-actuales', methods=['GET'])
@login_required
def api_datos_actuales():
    astra = AstraDB()
    datos_actuales = astra.get_data_real()
    return jsonify(datos_actuales)