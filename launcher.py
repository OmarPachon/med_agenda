# launcher.py
import os
import sys
import webbrowser
import subprocess
import time

# Cambiar al directorio del proyecto
os.chdir("C:\\med_agenda")

# Activar entorno virtual y ejecutar app.py en segundo plano
venv_python = "venv\\Scripts\\python.exe"
app_script = "app.py"

# Iniciar el servidor Flask en segundo plano (sin ventana)
flask_process = subprocess.Popen(
    [venv_python, app_script],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    creationflags=subprocess.CREATE_NO_WINDOW
)

# Esperar un poco para que el servidor se inicie
time.sleep(3)

# Abrir el navegador automáticamente
webbrowser.open("http://localhost:5000")

# Mantener el script vivo mientras el servidor corre
try:
    flask_process.wait()
except KeyboardInterrupt:
    flask_process.terminate()