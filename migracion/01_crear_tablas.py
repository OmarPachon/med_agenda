# migracion/01_crear_tablas.py
# Crea el esquema de la base de datos para Agendamiento-Med Elite

from db_config import get_connection
from utils import log_info, log_error

def crear_tablas():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        log_info("🔄 Iniciando creación de tablas...")
        
        # ========================================
        # 1. PACIENTES (desde bd_coosalud.txt)
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pacientes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tipo_documento VARCHAR(10) DEFAULT 'CC',
                numero_documento VARCHAR(30) NOT NULL UNIQUE,
                primer_nombre VARCHAR(50),
                segundo_nombre VARCHAR(50),
                primer_apellido VARCHAR(50),
                segundo_apellido VARCHAR(50),
                nombre_completo VARCHAR(150),
                fecha_nacimiento DATE,
                edad INT,
                genero ENUM('M', 'F', 'O'),
                regimen VARCHAR(50),
                tipo_afiliado VARCHAR(50),
                codigo_eps VARCHAR(20),
                departamento VARCHAR(50),
                ciudad VARCHAR(100),
                zona VARCHAR(50),
                direccion VARCHAR(200),
                telefono VARCHAR(20),
                email VARCHAR(100),
                fecha_afiliacion DATE,
                estado ENUM('AC', 'IN', 'OT') DEFAULT 'AC',
                carnet VARCHAR(100),
                INDEX idx_documento (numero_documento),
                INDEX idx_nombre (nombre_completo),
                INDEX idx_eps (codigo_eps)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        log_info("✅ Tabla 'pacientes' creada")
        
        # ========================================
        # 2. PROFESIONALES (desde Profesionales.txt)
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profesionales (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre_completo VARCHAR(150) NOT NULL UNIQUE,
                especialidad_1 VARCHAR(100),
                especialidad_2 VARCHAR(100),
                celular VARCHAR(20),
                estado ENUM('activo', 'inactivo') DEFAULT 'activo',
                INDEX idx_nombre (nombre_completo),
                INDEX idx_especialidad (especialidad_1)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        log_info("✅ Tabla 'profesionales' creada")
        
        # ========================================
        # 3. SERVICIOS (desde servicios.txt)
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS servicios (
                cups VARCHAR(20) PRIMARY KEY,
                hom_soat VARCHAR(20),
                nombre_servicio VARCHAR(200) NOT NULL,
                estado ENUM('activo', 'inactivo') DEFAULT 'activo',
                INDEX idx_nombre (nombre_servicio)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        log_info("✅ Tabla 'servicios' creada")
        
        # ========================================
        # 4. DIAGNOSTICOS (desde dx.txt)
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diagnosticos (
                codigo_cie VARCHAR(10) PRIMARY KEY,
                descripcion TEXT NOT NULL,
                INDEX idx_descripcion (descripcion(100)),
                INDEX idx_codigo (codigo_cie)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        log_info("✅ Tabla 'diagnosticos' creada")
        
        # ========================================
        # 5. AGENDA (desde agenda.csv) - TABLA PRINCIPAL
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agenda (
                id INT AUTO_INCREMENT PRIMARY KEY,
                
                -- Identificación del paciente
                tipo_documento VARCHAR(10),
                numero_documento VARCHAR(30),
                
                -- Fecha y hora de la cita
                fecha DATE NOT NULL,
                hora TIME NOT NULL,
                
                -- Información clínica
                cups VARCHAR(20),
                codigo_dx VARCHAR(10),
                dx_descripcion TEXT,
                
                -- Servicio y profesional
                nombre_servicio VARCHAR(200),
                nombre_profesional VARCHAR(150),
                
                -- Detalles de la terapia
                cantidad_total INT DEFAULT 0,
                frecuencia_semanal INT DEFAULT 0,
                duracion_meses INT DEFAULT 0,
                observaciones TEXT,
                
                -- Auditoría
                fecha_registro DATETIME,
                estado VARCHAR(20) DEFAULT 'activa',
                
                -- Claves foráneas (opcionales, pueden ser NULL)
                id_paciente INT,
                id_profesional INT,
                
                FOREIGN KEY (id_paciente) REFERENCES pacientes(id) ON DELETE SET NULL,
                FOREIGN KEY (id_profesional) REFERENCES profesionales(id) ON DELETE SET NULL,
                FOREIGN KEY (cups) REFERENCES servicios(cups) ON DELETE SET NULL,
                FOREIGN KEY (codigo_dx) REFERENCES diagnosticos(codigo_cie) ON DELETE SET NULL,
                
                -- Índices para búsquedas
                INDEX idx_fecha_hora (fecha, hora),
                INDEX idx_paciente (numero_documento),
                INDEX idx_profesional (nombre_profesional),
                INDEX idx_estado (estado),
                INDEX idx_fecha_estado (fecha, estado),
                
                -- Evitar duplicados exactos
                UNIQUE KEY unique_cita (numero_documento, fecha, hora, cups)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        log_info("✅ Tabla 'agenda' creada")
        
        # ========================================
        # 6. MIGRACION_LOG (para auditoría)
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migracion_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fecha_migracion DATETIME DEFAULT CURRENT_TIMESTAMP,
                archivo_origen VARCHAR(100),
                registros_procesados INT,
                registros_exitosos INT,
                registros_fallidos INT,
                estado ENUM('completada', 'parcial', 'fallida') DEFAULT 'completada',
                observaciones TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        log_info("✅ Tabla 'migracion_log' creada")
        
        conn.commit()
        
        log_info("🎉 ¡Todas las tablas creadas exitosamente!")
        print("\n📋 Tablas creadas:")
        print("   1. pacientes")
        print("   2. profesionales")
        print("   3. servicios")
        print("   4. diagnosticos")
        print("   5. agenda")
        print("   6. migracion_log")
        
        return True
        
    except Exception as e:
        if conn:
            conn.rollback()
        log_error(f"Error creando tablas: {str(e)}", "01_crear_tablas.py")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    crear_tablas()