@echo off
setlocal enabledelayedexpansion

echo.
echo 📦 Instalando Agendamiento-Med Elite v2.0...
echo © 2025 Omar Alberto Pachon Pereira
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  Este script requiere permisos de administrador.
    echo    Por favor, ejecuta este instalador como administrador.
    echo.
    pause
    exit /b 1
)

:: Crear directorio de instalación
set "INSTALL_DIR=C:\Program Files\Agendamiento-MedElite"
echo 📁 Creando directorio de instalación en: %INSTALL_DIR%
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Copiar archivos
echo 📤 Copiando archivos del sistema...
xcopy /E /I /Y "%~dp0*" "%INSTALL_DIR%\" >nul

:: Crear accesos directos
echo 🔗 Creando accesos directos...

:: Acceso directo en escritorio
set "DESKTOP=%USERPROFILE%\Desktop"
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%DESKTOP%\Agendamiento-Med Elite.lnk');$s.TargetPath='%INSTALL_DIR%\Agendamiento-MedElite.exe';$s.WorkingDirectory='%INSTALL_DIR%';$s.IconLocation='%INSTALL_DIR%\static\favicon.ico,0';$s.Description='Sistema de Gestión de Citas Médicas - © Omar Alberto Pachon Pereira';$s.Save()" >nul 2>&1

:: Acceso directo en menú de inicio
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%START_MENU%\Agendamiento-Med Elite.lnk');$s.TargetPath='%INSTALL_DIR%\Agendamiento-MedElite.exe';$s.WorkingDirectory='%INSTALL_DIR%';$s.IconLocation='%INSTALL_DIR%\static\favicon.ico,0';$s.Description='Sistema de Gestión de Citas Médicas - © Omar Alberto Pachon Pereira';$s.Save()" >nul 2>&1

:: Crear servicio (opcional - para ejecución automática)
echo ⚙️  Configurando el servicio del sistema...
sc create "AgendamientoMedElite" binPath= "\"%INSTALL_DIR%\Agendamiento-MedElite.exe\"" DisplayName= "Agendamiento-Med Elite Service" start= auto >nul 2>&1

:: Mensajes finales
echo.
echo ✅ Instalación completada exitosamente!
echo.
echo 💡 INSTRUCCIONES DE USO:
echo    1. Haz doble clic en el acceso directo 'Agendamiento-Med Elite' en tu escritorio
echo    2. Espera unos segundos mientras se inicia el servidor
echo    3. Abre tu navegador web en: http://localhost:5000
echo    4. ¡Listo! Tu sistema de agendamiento está listo para usar
echo.
echo 📞 SOPORTE:
echo    Desarrollador: Omar Alberto Pachon Pereira
echo    Versión: 2.0
echo    © 2025 Todos los derechos reservados
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
pause >nul