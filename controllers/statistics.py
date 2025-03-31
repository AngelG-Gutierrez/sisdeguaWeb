import os
from flask import Blueprint, Flask, render_template
from utils.auth_decorator import login_required
from database.astraDB import AstraDB
from flask import jsonify
from datetime import datetime

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

@statistics_db.route('/api/historicos', methods=['GET'])
@login_required
def obtener_datos_historicos():
    astra = AstraDB()
    datos_historicos = astra.get_sensor_data()

    datos_filtrados = [
        {
            "fecha": datetime.utcfromtimestamp(registro.get("date").timestamp_ms / 1000).isoformat(),
            "nivel_agua": registro.get("waterlevel"),
            "nivel_lluvia": registro.get("rainlevel")
        } 
        for registro in datos_historicos
    ]
    return jsonify(datos_filtrados)