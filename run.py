#!/usr/bin/env python3
"""
Agendamiento-Med Elite v2.0
Punto de entrada para empaquetado con PyInstaller

© 2025 Omar Alberto Pachon Pereira
"""
from app import app

if __name__ == "__main__":
    # Ejecutar en modo producción para el empaquetado
    app.run(debug=False, host="0.0.0.0", port=5000)