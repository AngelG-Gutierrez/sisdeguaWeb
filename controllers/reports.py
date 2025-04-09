from flask import Blueprint, render_template, Response
from utils.auth_decorator import login_required
from database.astraDB import AstraDB
import numpy as np
from datetime import datetime
from fpdf import FPDF
from flask_caching import Cache


reports_db = Blueprint('reports', __name__)
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

def init_cache(app):
    cache.init_app(app)

MESES_ESPANOL = {
    "January": "Enero", "February": "Febrero", "March": "Marzo",
    "April": "Abril", "May": "Mayo", "June": "Junio",
    "July": "Julio", "August": "Agosto", "September": "Septiembre",
    "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
}

def top_5_unique(values, reverse=False):
    return sorted(set(values), reverse=reverse)[:5]

def procesar_datos(data):
    reportes = {}
    for registro in data:
        fecha_obj = registro.get('date')
        nivel_agua = registro.get('waterlevel')
        lluvia = registro.get('rainlevel')

        if not fecha_obj or nivel_agua is None:
            continue

        try:
            fecha = datetime.fromtimestamp(fecha_obj.timestamp_ms / 1000.0)
            mes = MESES_ESPANOL[fecha.strftime("%B")]
        except Exception as e:
            print(f"Error al procesar fecha: {e}")
            continue

        if mes not in reportes:
            reportes[mes] = {'waterlevel': [], 'rainlevel': []}

        reportes[mes]['waterlevel'].append(nivel_agua)
        if lluvia is not None:
            reportes[mes]['rainlevel'].append(lluvia)

    return {
        mes: {
            'max': max(vals['waterlevel']) if vals['waterlevel'] else "Sin datos",
            'min': min(vals['waterlevel']) if vals['waterlevel'] else "Sin datos",
            'promedio': round(np.mean(vals['waterlevel']), 2) if vals['waterlevel'] else "Sin datos",
            'max_rain': max(vals['rainlevel']) if vals['rainlevel'] else "Sin datos",
            'min_rain': min(vals['rainlevel']) if vals['rainlevel'] else "Sin datos",
            'promedio_rain': round(np.mean(vals['rainlevel']), 2) if vals['rainlevel'] else "Sin datos",
            'top5_max': top_5_unique(vals['waterlevel'], reverse=True),
            'top5_min': top_5_unique(vals['waterlevel']),
            'top5_max_rain': top_5_unique(vals['rainlevel'], reverse=True),
            'top5_min_rain': top_5_unique(vals['rainlevel'])
        } for mes, vals in reportes.items()
    }

def obtener_reportes():
    cached_data = cache.get("reportes_mensuales")
    if cached_data:
        return cached_data

    db = AstraDB()
    data = db.get_sensor_data()
    reportes = procesar_datos(data) if data else {}

    cache.set("reportes_mensuales", reportes, timeout=300)
    return reportes

@reports_db.route('/reportes')
@login_required
def reportes():
    return render_template('reportes.html', reportes=obtener_reportes())

@reports_db.route('/descargar-pdf')
@login_required
def descargar_pdf():
    reportes_mensuales = obtener_reportes()

    pdf = FPDF()
    pdf.add_page()

    # Encabezado
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(63, 81, 181)
    pdf.cell(0, 15, "Reporte Mensual de Niveles", ln=True, align="C", fill=True)
    pdf.ln(10)

    def crear_tabla(mes, datos):
        pdf.set_font("Arial", 'B', 16)
        pdf.set_fill_color(197, 225, 165)
        pdf.set_text_color(0)
        pdf.cell(0, 12, mes.upper(), ln=True, align="C", fill=True)
        pdf.ln(5)

        pdf.set_fill_color(224, 247, 250)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(60, 10, "Categoría", 1, 0, 'C', fill=True)
        pdf.cell(40, 10, "Máximo", 1, 0, 'C', fill=True)
        pdf.cell(40, 10, "Mínimo", 1, 0, 'C', fill=True)
        pdf.cell(40, 10, "Promedio", 1, 1, 'C', fill=True)

        pdf.set_font("Arial", size=12)
        for categoria, clave in [("Nivel de Agua", ""), ("Nivel de Lluvia", "_rain")]:
            pdf.cell(60, 10, categoria, 1)
            pdf.cell(40, 10, str(datos[f'max{clave}']), 1)
            pdf.cell(40, 10, str(datos[f'min{clave}']), 1)
            pdf.cell(40, 10, str(datos[f'promedio{clave}']), 1)
            pdf.ln()
        pdf.ln(5)

        def top_list(titulo, lista):
            if not lista:
                return
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, titulo, ln=True)
            pdf.set_font("Arial", size=12)
            for i, val in enumerate(lista, start=1):
                pdf.cell(10, 8, f"{i}.", 0)
                pdf.cell(0, 8, str(val), ln=True)
            pdf.ln(3)

        top_list("Los 5 Niveles Más Altos de Agua", datos['top5_max'])
        top_list("Los 5 Niveles Más Bajos de Agua", datos['top5_min'])
        top_list("Los 5 Niveles Más Altos de Lluvia", datos['top5_max_rain'])
        top_list("Los 5 Niveles Más Bajos de Lluvia", datos['top5_min_rain'])

    for mes, datos in reportes_mensuales.items():
        crear_tabla(mes, datos)

    pdf.set_y(-20)
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, "Reporte generado automáticamente - Abril 2025", align="C")

    response = Response(pdf.output(dest='S').encode('latin1'), content_type='application/pdf')
    response.headers['Content-Disposition'] = 'attachment; filename=reportes_mensuales.pdf'
    return response