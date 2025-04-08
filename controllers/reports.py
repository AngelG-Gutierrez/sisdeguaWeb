from flask import Blueprint, render_template, Response
from utils.auth_decorator import login_required
from database.astraDB import AstraDB
import numpy as np
from datetime import datetime
from fpdf import FPDF

reports_db = Blueprint('reports', __name__)

def top_5_unique(values, reverse=False):
    unique_vals = sorted(set(values), reverse=reverse)
    return unique_vals[:5]

def procesar_datos(data):
    reportes = {}
    meses_espanol = {
        "January": "Enero", "February": "Febrero", "March": "Marzo",
        "April": "Abril", "May": "Mayo", "June": "Junio",
        "July": "Julio", "August": "Agosto", "September": "Septiembre",
        "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
    }

    for registro in data:
        fecha_obj = registro.get('date')
        nivel_agua = registro.get('waterlevel')
        lluvia = registro.get('rainlevel')

        if not fecha_obj or nivel_agua is None:
            continue

        try:
            fecha = datetime.fromtimestamp(fecha_obj.timestamp_ms / 1000.0)
        except Exception as e:
            print(f"Error al procesar fecha: {e}")
            continue

        mes = meses_espanol[fecha.strftime("%B")]
        if mes not in reportes:
            reportes[mes] = {'waterlevel': [], 'rainlevel': []}

        reportes[mes]['waterlevel'].append(nivel_agua)
        if lluvia is not None:
            reportes[mes]['rainlevel'].append(lluvia)

    reportes_finales = {}
    for mes, valores in reportes.items():
        agua = valores['waterlevel']
        lluvia = valores['rainlevel']

        reportes_finales[mes] = {
            'max': max(agua) if agua else "Sin datos",
            'min': min(agua) if agua else "Sin datos",
            'promedio': round(np.mean(agua), 2) if agua else "Sin datos",
            'max_rain': max(lluvia) if lluvia else "Sin datos",
            'min_rain': min(lluvia) if lluvia else "Sin datos",
            'promedio_rain': round(np.mean(lluvia), 2) if lluvia else "Sin datos",
            'top5_max': top_5_unique(agua, reverse=True),
            'top5_min': top_5_unique(agua),
            'top5_max_rain': top_5_unique(lluvia, reverse=True),
            'top5_min_rain': top_5_unique(lluvia)
        }

    return reportes_finales

@reports_db.route('/reportes')
@login_required
def reportes():
    db = AstraDB()
    data = db.get_sensor_data()
    reportes_mensuales = procesar_datos(data) if data else {}
    return render_template('reportes.html', reportes=reportes_mensuales)

@reports_db.route('/descargar-pdf')
@login_required
def descargar_pdf():
    db = AstraDB()
    data = db.get_sensor_data()
    reportes_mensuales = procesar_datos(data) if data else {}

    pdf = FPDF()
    pdf.add_page()

    # Encabezado principal
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(63, 81, 181)  # Azul moderno
    pdf.cell(0, 15, "Reporte Mensual de Niveles", ln=True, align="C", fill=True)
    pdf.ln(10)

    for mes, datos in reportes_mensuales.items():
        # Título del mes
        pdf.set_font("Arial", 'B', 16)
        pdf.set_fill_color(197, 225, 165)  # Verde claro
        pdf.cell(0, 12, mes.upper(), ln=True, align="C", fill=True)
        pdf.ln(5)

        # Tabla de datos
        pdf.set_fill_color(224, 247, 250)  # Azul muy claro
        pdf.set_text_color(0)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(60, 10, "Categoría", 1, 0, 'C', fill=True)
        pdf.cell(40, 10, "Máximo", 1, 0, 'C', fill=True)
        pdf.cell(40, 10, "Mínimo", 1, 0, 'C', fill=True)
        pdf.cell(40, 10, "Promedio", 1, 1, 'C', fill=True)

        # Datos de "Nivel de Agua"
        pdf.set_font("Arial", size=12)
        pdf.cell(60, 10, "Nivel de Agua", 1)
        pdf.cell(40, 10, str(datos['max']), 1)
        pdf.cell(40, 10, str(datos['min']), 1)
        pdf.cell(40, 10, str(datos['promedio']), 1)
        pdf.ln()

        # Datos de "Nivel de Lluvia"
        pdf.cell(60, 10, "Nivel de Lluvia", 1)
        pdf.cell(40, 10, str(datos['max_rain']), 1)
        pdf.cell(40, 10, str(datos['min_rain']), 1)
        pdf.cell(40, 10, str(datos['promedio_rain']), 1)
        pdf.ln(10)

        # Listas de Top 5 únicas
        def top_list(titulo, valores):
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(33, 33, 33)  # Gris oscuro
            pdf.cell(0, 8, titulo, ln=True)
            pdf.set_font("Arial", size=12)
            pdf.set_text_color(0)
            for i, val in enumerate(valores):
                pdf.cell(10, 8, f"{i+1}.", 0)
                pdf.cell(0, 8, str(val), ln=True)
            pdf.ln(3)

        top_list("Top 5 mayores únicos - Agua", datos.get('top5_max', []))
        top_list("Top 5 menores únicos - Agua", datos.get('top5_min', []))
        top_list("Top 5 mayores únicos - Lluvia", datos.get('top5_max_rain', []))
        top_list("Top 5 menores únicos - Lluvia", datos.get('top5_min_rain', []))
        pdf.ln(5)

    # Pie de página
    pdf.set_y(-20)
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, "Reporte generado automáticamente - Abril 2025", align="C")

    # Generación del PDF
    response = Response(pdf.output(dest='S').encode('latin1'), content_type='application/pdf')
    response.headers['Content-Disposition'] = 'attachment; filename=reportes_modernizados.pdf'
    return response