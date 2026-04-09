import pymysql

try:
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='med_elite_db',
        port=3306
    )
    print("✅ ¡Conexión exitosa a med_elite_db!")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")