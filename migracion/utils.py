# migracion/utils.py

import logging
from datetime import datetime
import os

# Configurar logging
LOG_FILE = os.path.join(os.path.dirname(__file__), 'migracion_reporte.log')

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def log_info(mensaje):
    logging.info(mensaje)
    print(f"ℹ️ {mensaje}")

def log_error(mensaje, archivo=None, linea=None):
    msg = f"[ERROR] {mensaje}"
    if archivo:
        msg += f" en {archivo}"
    if linea:
        msg += f" (Línea {linea})"
    logging.error(msg)
    print(f"❌ {msg}")

def log_warning(mensaje):
    logging.warning(mensaje)
    print(f"⚠️ {mensaje}")

def limpiar_texto(texto):
    """
    Limpia texto para BD. Convierte valores nulos a None.
    Maneja: #N/D, NULL, NONE, N/A, vacío, 'NULL', etc.
    """
    if texto is None:
        return None
    
    texto = str(texto).strip()
    
    # Lista de valores que deben ser NULL en la BD
    valores_nulos = [
        '', '#N/D', '#N/A', 'NULL', 'NONE', 'N/A', 'NULO', 
        'null', 'none', 'n/a', 'nulo', '-', '--', '...'
    ]
    
    if texto.upper() in [v.upper() for v in valores_nulos]:
        return None
    
    # Codificar y decodificar para limpiar caracteres especiales
    try:
        return texto.encode('utf-8').decode('utf-8')
    except:
        return texto

def validar_documento(doc):
    """Valida que el documento no esté vacío"""
    doc = limpiar_texto(doc)
    if not doc:
        return None
    return doc

def convertir_fecha_yyyy_mm_dd(fecha_str):
    """Convierte YYYY/MM/DD a YYYY-MM-DD"""
    if not fecha_str:
        return None
    try:
        fecha_str = str(fecha_str).strip()
        if fecha_str.upper() in ['#N/D', 'NULL', 'NONE', 'N/A', '']:
            return None
        if '/' in fecha_str:
            partes = fecha_str.split('/')
            return f"{partes[0]}-{partes[1].zfill(2)}-{partes[2].zfill(2)}"
        return fecha_str
    except:
        return None

def validar_fecha(fecha_str, formato='%Y-%m-%d'):
    """Valida y convierte string a date"""
    if not fecha_str or str(fecha_str).strip() == '':
        return None
    try:
        return datetime.strptime(str(fecha_str).strip(), formato).date()
    except ValueError:
        return None

def validar_hora(hora_str):
    """Valida y convierte string a time"""
    if not hora_str or str(hora_str).strip() == '':
        return None
    try:
        return datetime.strptime(str(hora_str).strip(), '%H:%M').time()
    except ValueError:
        try:
            return datetime.strptime(str(hora_str).strip(), '%H:%M:%S').time()
        except ValueError:
            return None