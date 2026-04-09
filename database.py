# database.py
# Conexión a MySQL con fallback a CSV para Agendamiento-Med Elite

import pymysql
from datetime import datetime, date
import os

# Configuración de MySQL
MYSQL_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'med_elite_db',
    'port': 3306,
    'charset': 'utf8mb4'
}

def get_connection():
    """Obtiene conexión a MySQL o None si falla"""
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        return conn
    except Exception as e:
        print(f"⚠️ MySQL no disponible: {e}")
        return None

def test_mysql():
    """Prueba si MySQL está disponible"""
    conn = get_connection()
    if conn:
        conn.close()
        return True
    return False

# ============================================
# FUNCIONES DE LECTURA (MySQL → Fallback CSV)
# ============================================

def obtener_pacientes_activos():
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT tipo_documento, numero_documento, primer_nombre, segundo_nombre,
                   primer_apellido, segundo_apellido, nombre_completo,
                   fecha_nacimiento, genero, regimen, tipo_afiliado, codigo_eps,
                   departamento, ciudad, zona, estado
            FROM pacientes
            WHERE estado = 'AC'
        """)
        pacientes = cursor.fetchall()
        cursor.close()
        conn.close()
        return pacientes
    except Exception as e:
        print(f"Error obteniendo pacientes: {e}")
        return None

def obtener_paciente_por_documento(tipo_doc, num_doc):
    """Busca paciente por documento"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT tipo_documento, numero_documento, primer_nombre, segundo_nombre,
                   primer_apellido, segundo_apellido, fecha_nacimiento, genero,
                   regimen, tipo_afiliado, codigo_eps, departamento, ciudad, zona, estado
            FROM pacientes
            WHERE tipo_documento = %s AND numero_documento = %s
        """, (tipo_doc, num_doc))
        paciente = cursor.fetchone()
        cursor.close()
        conn.close()
        return paciente
    except Exception as e:
        print(f"Error buscando paciente: {e}")
        return None

def obtener_dx():
    """Obtiene diagnósticos desde MySQL"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT codigo_cie, descripcion FROM diagnosticos")
        dx = {row['codigo_cie']: row['descripcion'] for row in cursor.fetchall()}
        cursor.close()
        conn.close()
        return dx
    except Exception as e:
        print(f"Error obteniendo dx: {e}")
        return None

def obtener_servicios():
    """Obtiene servicios desde MySQL"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT cups, nombre_servicio FROM servicios WHERE estado = 'activo'")
        servicios = {row['cups']: row['nombre_servicio'] for row in cursor.fetchall()}
        cursor.close()
        conn.close()
        return servicios
    except Exception as e:
        print(f"Error obteniendo servicios: {e}")
        return None

def obtener_profesionales():
    """Obtiene profesionales desde MySQL"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT nombre_completo, especialidad_1, especialidad_2, celular
            FROM profesionales
            WHERE estado = 'activo'
            ORDER BY nombre_completo
        """)
        profesionales = cursor.fetchall()
        cursor.close()
        conn.close()
        return profesionales
    except Exception as e:
        print(f"Error obteniendo profesionales: {e}")
        return None

def obtener_celular_profesional(nombre_profesional):
    """Obtiene celular de un profesional"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT celular FROM profesionales
            WHERE nombre_completo = %s
        """, (nombre_profesional,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result['celular'] if result else None
    except Exception as e:
        print(f"Error obteniendo celular: {e}")
        return None

def obtener_agenda_activa(fecha=None, profesional=None, limit=100):
    """Obtiene agenda activa desde MySQL"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        query = """
            SELECT a.*, p.nombre_completo as paciente_nombre
            FROM agenda a
            LEFT JOIN pacientes p ON a.numero_documento = p.numero_documento
            WHERE a.estado = 'activa'
        """
        params = []
        
        if fecha:
            query += " AND a.fecha = %s"
            params.append(fecha)
        
        if profesional:
            query += " AND a.nombre_profesional = %s"
            params.append(profesional)
        
        query += " ORDER BY a.fecha, a.hora LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        agenda = cursor.fetchall()
        cursor.close()
        conn.close()
        return agenda
    except Exception as e:
        print(f"Error obteniendo agenda: {e}")
        return None

def contar_sesiones_realizadas(tipo_doc, num_doc, cups):
    """Cuenta sesiones realizadas de una terapia"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM agenda
            WHERE numero_documento = %s AND cups = %s AND estado = 'activa'
        """, (num_doc, cups))
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except Exception as e:
        print(f"Error contando sesiones: {e}")
        return None

# ============================================
# FUNCIONES DE ESCRITURA (CSV + MySQL)
# ============================================

def crear_cita_mysql(datos):
    """Crea una cita en MySQL"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agenda (
                tipo_documento, numero_documento, fecha, hora,
                cups, codigo_dx, dx_descripcion,
                nombre_servicio, nombre_profesional,
                cantidad_total, frecuencia_semanal, duracion_meses,
                observaciones, fecha_registro, estado
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            datos.get('tipo_documento', 'RC'),
            datos.get('numero_documento'),
            datos.get('fecha'),
            datos.get('hora'),
            datos.get('cups'),
            datos.get('codigo_dx'),
            datos.get('dx_descripcion'),
            datos.get('nombre_servicio'),
            datos.get('nombre_profesional'),
            datos.get('cantidad_total', 0),
            datos.get('frecuencia_semanal', 0),
            datos.get('duracion_meses', 0),
            datos.get('observaciones', ''),
            datos.get('fecha_registro', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            datos.get('estado', 'activa')
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creando cita en MySQL: {e}")
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return False

def actualizar_estado_cita(tipo_doc, num_doc, profesional, fecha, hora, cups, nuevo_estado):
    """Actualiza el estado de una cita (cancelar, no_asistio)"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE agenda
            SET estado = %s
            WHERE numero_documento = %s AND nombre_profesional = %s 
              AND fecha = %s AND hora = %s AND cups = %s
        """, (nuevo_estado, num_doc, profesional, fecha, hora, cups))
        conn.commit()
        afectadas = cursor.rowcount
        cursor.close()
        conn.close()
        return afectadas > 0
    except Exception as e:
        print(f"Error actualizando estado: {e}")
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return False

def crear_paciente_mysql(datos):
    """Crea un paciente en MySQL (si no existe)"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT IGNORE INTO pacientes (
                tipo_documento, numero_documento, primer_nombre, segundo_nombre,
                primer_apellido, segundo_apellido, nombre_completo,
                fecha_nacimiento, genero, regimen, tipo_afiliado,
                codigo_eps, departamento, ciudad, zona, estado
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            datos.get('tipo_documento', 'CC'),
            datos.get('numero_documento'),
            datos.get('primer_nombre', ''),
            datos.get('segundo_nombre', ''),
            datos.get('primer_apellido', ''),
            datos.get('segundo_apellido', ''),
            datos.get('nombre_completo', ''),
            datos.get('fecha_nacimiento'),
            datos.get('genero', 'M'),
            datos.get('regimen', ''),
            datos.get('tipo_afiliado', ''),
            datos.get('codigo_eps', ''),
            datos.get('departamento', ''),
            datos.get('ciudad', ''),
            datos.get('zona', ''),
            datos.get('estado', 'AC')
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creando paciente en MySQL: {e}")
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return False

# ============================================
# FUNCIONES DE ADMINISTRACIÓN
# ============================================

def agregar_dx_mysql(codigo, descripcion):
    """Agrega un diagnóstico"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT IGNORE INTO diagnosticos (codigo_cie, descripcion)
            VALUES (%s, %s)
        """, (codigo, descripcion))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error agregando dx: {e}")
        return False

def eliminar_dx_mysql(codigo):
    """Elimina un diagnóstico"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM diagnosticos WHERE codigo_cie = %s", (codigo,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error eliminando dx: {e}")
        return False

def agregar_servicio_mysql(cups, hom_soat, nombre):
    """Agrega un servicio"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT IGNORE INTO servicios (cups, hom_soat, nombre_servicio)
            VALUES (%s, %s, %s)
        """, (cups, hom_soat, nombre))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error agregando servicio: {e}")
        return False

def agregar_profesional_mysql(nombre, esp1, esp2, celular):
    """Agrega un profesional"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT IGNORE INTO profesionales (nombre_completo, especialidad_1, especialidad_2, celular)
            VALUES (%s, %s, %s, %s)
        """, (nombre, esp1, esp2, celular))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error agregando profesional: {e}")
        return False

def actualizar_celular_profesional(nombre, celular):
    """Actualiza celular de profesional"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE profesionales SET celular = %s WHERE nombre_completo = %s
        """, (celular, nombre))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error actualizando celular: {e}")
        return False