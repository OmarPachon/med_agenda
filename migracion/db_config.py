# migracion/db_config.py

import pymysql

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'med_elite_db',
    'port': 3306,
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_connection():
    """Retorna conexión a med_elite_db"""
    return pymysql.connect(**DB_CONFIG)

def get_connection_without_db():
    """Retorna conexión sin BD seleccionada"""
    config = DB_CONFIG.copy()
    config.pop('database')
    return pymysql.connect(**config)