import os
import time
import shutil
import csv
from datetime import datetime

class FileLock:
    """Bloqueo exclusivo para evitar que dos procesos escriban a la vez."""
    def __init__(self, filepath, timeout=10):
        self.filepath = filepath
        self.lockfile = filepath + ".lock"
        self.timeout = timeout

    def acquire(self):
        start_time = time.time()
        while True:
            try:
                # Intentar crear el archivo .lock exclusivamente
                fd = os.open(self.lockfile, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                return True
            except FileExistsError:
                # Si existe, verificamos si es viejo (proceso muerto)
                try:
                    if time.time() - os.path.getmtime(self.lockfile) > self.timeout:
                        os.remove(self.lockfile)
                        continue
                except OSError:
                    pass
                if time.time() - start_time > self.timeout:
                    raise TimeoutError(f"Timeout esperando lock para {self.filepath}")
                time.sleep(0.1)

    def release(self):
        try:
            os.remove(self.lockfile)
        except OSError:
            pass

def safe_csv_rewrite(filepath, rows, fieldnames):
    """
    Reemplaza TODO el contenido del CSV de forma segura.
    Usado para: editar, eliminar, actualizar estados, limpiar agenda.
    1. Backup -> 2. Lock -> 3. Escribir todo -> 4. Unlock
    """
    backup_dir = "data/backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # 1. Backup
    if os.path.exists(filepath):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(filepath)
        backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}.bak")
        shutil.copy2(filepath, backup_path)

    # 2. Lock y Escritura
    lock = FileLock(filepath)
    try:
        lock.acquire()
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    finally:
        lock.release()

def safe_csv_append(filepath, row_dict, fieldnames):
    """
    Agrega UNA fila de forma segura.
    Usado para: guardar cita simple, guardar cita bloque.
    1. Backup -> 2. Lock -> 3. Leer todo -> 4. Agregar fila -> 5. Reescribir todo -> 6. Unlock
    (Reescribir todo es más seguro que append puro con locks)
    """
    backup_dir = "data/backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # 1. Backup
    if os.path.exists(filepath):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(filepath)
        backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}.bak")
        shutil.copy2(filepath, backup_path)

    # 2. Lock y Escritura
    lock = FileLock(filepath)
    try:
        lock.acquire()
        
        # Leer existente
        rows = []
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        
        # Agregar nueva
        rows.append(row_dict)

        # Reescribir todo
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    finally:
        lock.release()

def safe_csv_append_multiple(filepath, list_of_rows, fieldnames):
    """
    Agrega MÚLTIPLES filas de una vez (atómico).
    Usado para: carga masiva, citas concentradas.
    """
    backup_dir = "data/backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # 1. Backup
    if os.path.exists(filepath):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(filepath)
        backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}.bak")
        shutil.copy2(filepath, backup_path)

    # 2. Lock y Escritura
    lock = FileLock(filepath)
    try:
        lock.acquire()
        
        rows = []
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        
        # Agregar todas las nuevas
        rows.extend(list_of_rows)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    finally:
        lock.release()