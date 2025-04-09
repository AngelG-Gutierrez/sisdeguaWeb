import os
from flask import Blueprint, Flask, render_template
from utils.auth_decorator import login_required
from database.astraDB import AstraDB
from flask import jsonify
from datetime import datetime, timezone, timedelta

statistics_db = Blueprint('statistics', __name__)
app = Flask(__name__, template_folder=os.path.join('templates')) 

@statistics_db.route('/statistics', methods=['GET', 'POST'])
@login_required
def statistics():
    #astra = AstraDB()
    #datos_actuales = astra.get_data_real()
    #datos_historicos = astra.get_sensor_data()
    return render_template('estadisticas.html')
    #datos_actuales=datos_actuales,
    #datos_historicos=datos_historicos)

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


@statistics_db.route('/api/tablee', methods=['GET'])
@login_required
def obtener_datos():
    astra = AstraDB()
    datos_historicos = astra.get_sensor_data()

    hoy = datetime.now(timezone.utc).date()
    fecha_limite = hoy - timedelta(days=27)

    agrupados_por_fecha = {}

    for registro in datos_historicos:
        timestamp_ms = registro.get("date").timestamp_ms
        fecha = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).date()

        if fecha >= fecha_limite:
            clave = fecha.isoformat()

            if clave not in agrupados_por_fecha:
                agrupados_por_fecha[clave] = {
                    "agua_total": 0,
                    "lluvia_total": 0,
                    "conteo": 0
                }

            agrupados_por_fecha[clave]["agua_total"] += registro.get("waterlevel", 0)
            agrupados_por_fecha[clave]["lluvia_total"] += registro.get("rainlevel", 0)
            agrupados_por_fecha[clave]["conteo"] += 1

    # Calcular promedios
    datos_finales = []
    for fecha in sorted(agrupados_por_fecha.keys()):
        total = agrupados_por_fecha[fecha]
        promedio_agua = total["agua_total"] / total["conteo"]
        promedio_lluvia = total["lluvia_total"] / total["conteo"]

        datos_finales.append({
            "fecha": fecha,
            "nivel_agua": round(promedio_agua, 2),
            "nivel_lluvia": round(promedio_lluvia, 2)
        })

    return jsonify(datos_finales)