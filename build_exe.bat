@echo off
echo ==========================================
echo    CREANDO EJECUTABLE (.EXE) PARA SHERLOCK
echo ==========================================
echo.
echo 1. Instalando dependencias necesarias...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo 2. Compilando aplicacion (esto puede tardar unos minutos)...
python -m PyInstaller --noconfirm --onefile --windowed --name "SherlockOSINT" --add-data "../resources;resources" --add-data "../__init__.py;sherlock_project" --add-data "../sherlock.py;sherlock_project" --add-data "../sites.py;sherlock_project" --add-data "../result.py;sherlock_project" --add-data "../notify.py;sherlock_project" native_app.py

echo.
echo ==========================================
echo    PROCESO FINALIZADO
echo ==========================================
echo El archivo .exe se encuentra en la carpeta:
echo [sherlock-gui\dist\SherlockOSINT.exe]
echo.
pause
