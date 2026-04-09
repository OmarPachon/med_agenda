# migracion/02_migrar_datos.py
# VERSIÓN DEFINITIVA - Manejo robusto de datos grandes

import csv
import os
import pymysql
from datetime import datetime
from db_config import get_connection
from utils import log_info, log_error, log_warning, limpiar_texto, convertir_fecha_yyyy_mm_dd

# ⬇️ CRÍTICO: Aumentar límite de campo CSV
csv.field_size_limit(500 * 1024 * 1024)  # 500 MB

# Rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# ⬇️ CRÍTICO: Lotes MUY pequeños para evitar crash
BATCH_SIZE = 20  # Commit cada 20 registros (más seguro)

def migrar_diagnosticos(conn):
    cursor = conn.cursor()
    archivo = os.path.join(DATA_DIR, 'dx.txt')
    
    if not os.path.exists(archivo):
        log_error("Archivo no encontrado: dx.txt", "02_migrar_datos.py")
        return 0, 0
    
    log_info("📄 Migrando diagnósticos (dx.txt)...")
    
    exitosos = 0
    fallidos = 0
    
    try:
        with open(archivo, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f, delimiter='|')
            
            for i, row in enumerate(reader, start=2):
                try:
                    codigo = limpiar_texto(row.get('Dx'))
                    descripcion = limpiar_texto(row.get('DIAGNOSTICO'))
                    
                    if not codigo or not descripcion:
                        fallidos += 1
                        continue
                    
                    # Truncar descripción muy larga
                    if descripcion and len(descripcion) > 500:
                        descripcion = descripcion[:500]
                    
                    cursor.execute("""
                        INSERT IGNORE INTO diagnosticos (codigo_cie, descripcion)
                        VALUES (%s, %s)
                    """, (codigo, descripcion))
                    
                    exitosos += 1
                    
                    if exitosos % BATCH_SIZE == 0:
                        conn.commit()
                    
                except Exception as e:
                    log_error(f"Línea {i}: {str(e)[:100]}", "dx.txt")
                    fallidos += 1
        
        conn.commit()
        log_info(f"✅ Diagnósticos: {exitosos} exitosos, {fallidos} fallidos")
        return exitosos, fallidos
        
    except Exception as e:
        conn.rollback()
        log_error(f"Error migrando diagnósticos: {str(e)}", "02_migrar_datos.py")
        raise

def migrar_servicios(conn):
    cursor = conn.cursor()
    archivo = os.path.join(DATA_DIR, 'servicios.txt')
    
    if not os.path.exists(archivo):
        log_error("Archivo no encontrado: servicios.txt", "02_migrar_datos.py")
        return 0, 0
    
    log_info("📄 Migrando servicios (servicios.txt)...")
    
    exitosos = 0
    fallidos = 0
    
    try:
        with open(archivo, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f, delimiter='|')
            
            for i, row in enumerate(reader, start=2):
                try:
                    cups = limpiar_texto(row.get('CUPS_ISS'))
                    hom_soat = limpiar_texto(row.get('HOM_SOAT'))
                    nombre = limpiar_texto(row.get('SERVICIO'))
                    
                    if not cups or not nombre:
                        fallidos += 1
                        continue
                    
                    if nombre and len(nombre) > 200:
                        nombre = nombre[:200]
                    
                    cursor.execute("""
                        INSERT IGNORE INTO servicios (cups, hom_soat, nombre_servicio)
                        VALUES (%s, %s, %s)
                    """, (cups, hom_soat, nombre))
                    
                    exitosos += 1
                    
                    if exitosos % BATCH_SIZE == 0:
                        conn.commit()
                    
                except Exception as e:
                    log_error(f"Línea {i}: {str(e)[:100]}", "servicios.txt")
                    fallidos += 1
        
        conn.commit()
        log_info(f"✅ Servicios: {exitosos} exitosos, {fallidos} fallidos")
        return exitosos, fallidos
        
    except Exception as e:
        conn.rollback()
        log_error(f"Error migrando servicios: {str(e)}", "02_migrar_datos.py")
        raise

def migrar_profesionales(conn):
    cursor = conn.cursor()
    archivo = os.path.join(DATA_DIR, 'Profesionales.txt')
    
    if not os.path.exists(archivo):
        log_error("Archivo no encontrado: Profesionales.txt", "02_migrar_datos.py")
        return 0, 0
    
    log_info("📄 Migrando profesionales (Profesionales.txt)...")
    
    exitosos = 0
    fallidos = 0
    
    try:
        with open(archivo, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f, delimiter='|')
            
            for i, row in enumerate(reader, start=2):
                try:
                    nombre = limpiar_texto(row.get('Profesional'))
                    esp1 = limpiar_texto(row.get('Especialidad_1'))
                    esp2 = limpiar_texto(row.get('Especialidad_2'))
                    celular = limpiar_texto(row.get('Celular'))
                    
                    if not nombre:
                        fallidos += 1
                        continue
                    
                    cursor.execute("""
                        INSERT IGNORE INTO profesionales 
                        (nombre_completo, especialidad_1, especialidad_2, celular)
                        VALUES (%s, %s, %s, %s)
                    """, (nombre, esp1, esp2, celular))
                    
                    exitosos += 1
                    
                    if exitosos % BATCH_SIZE == 0:
                        conn.commit()
                    
                except Exception as e:
                    log_error(f"Línea {i}: {str(e)[:100]}", "Profesionales.txt")
                    fallidos += 1
        
        conn.commit()
        log_info(f"✅ Profesionales: {exitosos} exitosos, {fallidos} fallidos")
        return exitosos, fallidos
        
    except Exception as e:
        conn.rollback()
        log_error(f"Error migrando profesionales: {str(e)}", "02_migrar_datos.py")
        raise

def migrar_pacientes(conn):
    """Migración de pacientes con manejo robusto de campos grandes"""
    cursor = conn.cursor()
    archivo = os.path.join(DATA_DIR, 'bd_coosalud.txt')
    
    if not os.path.exists(archivo):
        log_error("Archivo no encontrado: bd_coosalud.txt", "02_migrar_datos.py")
        return 0, 0
    
    log_info("📄 Migrando pacientes (bd_coosalud.txt)...")
    log_info(f"   📦 Tamaño de lote: {BATCH_SIZE} registros (seguro)")
    
    exitosos = 0
    fallidos = 0
    linea_numero = 1
    
    try:
        with open(archivo, 'r', encoding='utf-8', errors='replace') as f:
            lineas = f.readlines()
            
            if not lineas:
                log_error("Archivo vacío: bd_coosalud.txt", "02_migrar_datos.py")
                return 0, 0
            
            encabezados = lineas[0].strip().split('|')
            log_info(f"   📋 Columnas: {len(encabezados)}")
            log_info(f"   📊 Total líneas: {len(lineas) - 1}")
            
            for linea_numero, linea in enumerate(lineas[1:], start=2):
                try:
                    if not linea.strip():
                        continue
                    
                    # ⬇️ CRÍTICO: Leer línea manualmente para evitar error de campo grande
                    valores = linea.strip().split('|')
                    row = dict(zip(encabezados, valores))
                    
                    tipo_doc = limpiar_texto(row.get('Tipo_Documento'))
                    num_doc = limpiar_texto(row.get('Numero_Documento'))
                    
                    if not num_doc or num_doc == '#N/D':
                        fallidos += 1
                        continue
                    
                    fecha_nac = convertir_fecha_yyyy_mm_dd(row.get('Fecha_Nacimiento'))
                    fecha_afil = convertir_fecha_yyyy_mm_dd(row.get('Fecha_Afiliacion'))
                    
                    primer_nombre = limpiar_texto(row.get('Primer_Nombre')) or ''
                    segundo_nombre = limpiar_texto(row.get('Segundo_Nombre')) or ''
                    primer_apellido = limpiar_texto(row.get('Primer_Apellido')) or ''
                    segundo_apellido = limpiar_texto(row.get('Segundo_Apellido')) or ''
                    
                    nombre_completo = f"{primer_nombre} {segundo_nombre} {primer_apellido} {segundo_apellido}".strip()
                    
                    # ⬇️ CRÍTICO: Truncar campos largos para evitar packet limit
                    direccion = limpiar_texto(row.get('DIRECCION'))
                    if direccion and len(direccion) > 100:
                        direccion = direccion[:100]
                    
                    # Truncar otros campos potencialmente largos
                    ciudad = limpiar_texto(row.get('Ciudad'))
                    if ciudad and len(ciudad) > 50:
                        ciudad = ciudad[:50]
                    
                    cursor.execute("""
                        INSERT IGNORE INTO pacientes (
                            tipo_documento, numero_documento, primer_nombre, segundo_nombre,
                            primer_apellido, segundo_apellido, nombre_completo,
                            fecha_nacimiento, edad, genero, regimen, tipo_afiliado,
                            codigo_eps, departamento, ciudad, zona, direccion,
                            telefono, email, fecha_afiliacion, estado, carnet
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        tipo_doc or 'CC',
                        num_doc,
                        primer_nombre,
                        segundo_nombre,
                        primer_apellido,
                        segundo_apellido,
                        nombre_completo,
                        fecha_nac,
                        limpiar_texto(row.get('EDAD')),
                        limpiar_texto(row.get('Genero')),
                        limpiar_texto(row.get('REGIMEN')),
                        limpiar_texto(row.get('TIPO_AFILIADO')),
                        limpiar_texto(row.get('Codigo_EPS')),
                        limpiar_texto(row.get('Departamento')),
                        ciudad,
                        limpiar_texto(row.get('Zona')),
                        direccion,
                        limpiar_texto(row.get('TELEFONO')),
                        limpiar_texto(row.get('Email')),
                        fecha_afil,
                        limpiar_texto(row.get('Estado')),
                        limpiar_texto(row.get('CARNET'))
                    ))
                    
                    exitosos += 1
                    
                    # ⬇️ CRÍTICO: Commit MUY frecuente
                    if exitosos % BATCH_SIZE == 0:
                        conn.commit()
                        log_info(f"   ⏳ ... {exitosos} pacientes procesados (commit)")
                    
                except Exception as e:
                    log_error(f"Línea {linea_numero}: {str(e)[:100]}", "bd_coosalud.txt")
                    fallidos += 1
                    continue
        
        # Commit final
        conn.commit()
        
        log_info(f"✅ Pacientes: {exitosos} exitosos, {fallidos} fallidos")
        return exitosos, fallidos
        
    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        log_error(f"Error migrando pacientes (línea {linea_numero}): {str(e)}", "02_migrar_datos.py")
        raise

def migrar_agenda(conn):
    cursor = conn.cursor()
    archivo = os.path.join(DATA_DIR, 'agenda.csv')
    
    if not os.path.exists(archivo):
        log_error("Archivo no encontrado: agenda.csv", "02_migrar_datos.py")
        return 0, 0
    
    log_info("📄 Migrando agenda (agenda.csv)...")
    
    exitosos = 0
    fallidos = 0
    
    try:
        with open(archivo, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f, delimiter=',')
            
            for i, row in enumerate(reader, start=2):
                try:
                    num_doc = limpiar_texto(row.get('Num_Doc'))
                    fecha_str = limpiar_texto(row.get('Fecha'))
                    hora_str = limpiar_texto(row.get('Hora'))
                    
                    if not num_doc or not fecha_str or not hora_str:
                        fallidos += 1
                        continue
                    
                    # Validar fecha
                    try:
                        datetime.strptime(fecha_str, '%Y-%m-%d')
                    except ValueError:
                        log_error(f"Línea {i}: Fecha inválida '{fecha_str}'", "agenda.csv")
                        fallidos += 1
                        continue
                    
                    # Validar hora
                    try:
                        if len(hora_str) == 5:
                            datetime.strptime(hora_str, '%H:%M')
                        else:
                            datetime.strptime(hora_str, '%H:%M:%S')
                    except ValueError:
                        log_error(f"Línea {i}: Hora inválida '{hora_str}'", "agenda.csv")
                        fallidos += 1
                        continue
                    
                    # ⬇️ CRÍTICO: Truncar campos largos
                    observacion = limpiar_texto(row.get('Observacion'))
                    if observacion and len(observacion) > 200:
                        observacion = observacion[:200]
                    
                    dx_desc = limpiar_texto(row.get('Dx_Descripcion'))
                    if dx_desc and len(dx_desc) > 300:
                        dx_desc = dx_desc[:300]
                    
                    cursor.execute("""
                        INSERT IGNORE INTO agenda (
                            tipo_documento, numero_documento, fecha, hora,
                            cups, codigo_dx, dx_descripcion,
                            nombre_servicio, nombre_profesional,
                            cantidad_total, frecuencia_semanal, duracion_meses,
                            observaciones, fecha_registro, estado
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        limpiar_texto(row.get('Tipo_Doc')) or 'RC',
                        num_doc,
                        fecha_str,
                        hora_str,
                        limpiar_texto(row.get('CUPS')),
                        limpiar_texto(row.get('Dx_Codigo')),
                        dx_desc,
                        limpiar_texto(row.get('Servicio')),
                        limpiar_texto(row.get('Profesional')),
                        int(limpiar_texto(row.get('Cantidad_Total')) or 0),
                        int(limpiar_texto(row.get('Frecuencia_Semanal')) or 0),
                        int(limpiar_texto(row.get('Duracion_Meses')) or 0),
                        observacion,
                        limpiar_texto(row.get('Fecha_Registro')),
                        limpiar_texto(row.get('Estado')) or 'activa'
                    ))
                    
                    exitosos += 1
                    
                    if exitosos % BATCH_SIZE == 0:
                        conn.commit()
                        log_info(f"   ⏳ ... {exitosos} citas procesadas (commit)")
                    
                except Exception as e:
                    log_error(f"Línea {i}: {str(e)[:100]}", "agenda.csv")
                    fallidos += 1
        
        conn.commit()
        log_info(f"✅ Agenda: {exitosos} exitosos, {fallidos} fallidos")
        return exitosos, fallidos
        
    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        log_error(f"Error migrando agenda: {str(e)}", "02_migrar_datos.py")
        raise

def registrar_migracion(conn, archivo, procesados, exitosos, fallidos, estado):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO migracion_log 
            (archivo_origen, registros_procesados, registros_exitosos, registros_fallidos, estado)
            VALUES (%s, %s, %s, %s, %s)
        """, (archivo, procesados, exitosos, fallidos, estado))
        conn.commit()
    except Exception as e:
        log_warning(f"No se pudo registrar el log: {str(e)[:50]}")

def main():
    log_info("=" * 60)
    log_info("🚀 INICIANDO MIGRACIÓN COMPLETA - Agendamiento Med Elite")
    log_info("=" * 60)
    
    conn = None
    resumen = {}
    
    try:
        conn = get_connection()
        
        # ⬇️ CRÍTICO: Configurar sesión MySQL para evitar timeout (SIN max_allowed_packet)
        cursor = conn.cursor()
        cursor.execute("SET SESSION wait_timeout=28800")
        cursor.execute("SET SESSION interactive_timeout=28800")
        # max_allowed_packet se maneja con BATCH_SIZE pequeño (20 registros)
        cursor.close()
        log_info("✅ Configuración de sesión MySQL aplicada (timeout)")
        
        migraciones = [
            ('diagnosticos', migrar_diagnosticos),
            ('servicios', migrar_servicios),
            ('profesionales', migrar_profesionales),
            ('pacientes', migrar_pacientes),
            ('agenda', migrar_agenda),
        ]
        
        for nombre, funcion in migraciones:
            log_info(f"\n{'─' * 60}")
            try:
                exitosos, fallidos = funcion(conn)
                total = exitosos + fallidos
                estado = 'completada' if fallidos == 0 else 'parcial'
                resumen[nombre] = {'total': total, 'exitosos': exitosos, 'fallidos': fallidos}
                registrar_migracion(conn, f"{nombre}.txt/csv", total, exitosos, fallidos, estado)
            except Exception as e:
                log_error(f"Migración de {nombre} FALLÓ: {str(e)[:100]}", "main")
                resumen[nombre] = {'total': 0, 'exitosos': 0, 'fallidos': 0, 'error': str(e)}
                registrar_migracion(conn, f"{nombre}.txt/csv", 0, 0, 0, 'fallida')
                # Continuar con las demás tablas en lugar de detener todo
                continue
        
        log_info("\n" + "=" * 60)
        log_info("📊 RESUMEN FINAL DE MIGRACIÓN")
        log_info("=" * 60)
        
        total_general = sum(d.get('total', 0) for d in resumen.values())
        exitosos_general = sum(d.get('exitosos', 0) for d in resumen.values())
        fallidos_general = sum(d.get('fallidos', 0) for d in resumen.values())
        
        for nombre, datos in resumen.items():
            log_info(f"   {nombre:15} │ Total: {datos.get('total', 0):5} │ Exitosos: {datos.get('exitosos', 0):5} │ Fallidos: {datos.get('fallidos', 0):5}")
        
        log_info("-" * 60)
        log_info(f"   {'TOTAL':15} │ Total: {total_general:5} │ Exitosos: {exitosos_general:5} │ Fallidos: {fallidos_general:5}")
        log_info("=" * 60)
        
        if fallidos_general == 0:
            log_info("🎉 ¡MIGRACIÓN COMPLETADA CON ÉXITO!")
        else:
            log_warning(f"⚠️ MIGRACIÓN COMPLETADA CON {fallidos_general} REGISTROS FALLIDOS")
            log_info("📄 Revisa 'migracion_reporte.log' para detalles")
        
    except Exception as e:
        log_error(f"Migración fallida: {str(e)}", "main")
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass
        log_info("🔒 Conexión cerrada")

if __name__ == "__main__":
    main()