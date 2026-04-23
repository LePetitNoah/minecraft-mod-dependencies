@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo.
echo ================================
echo  Installation - Minecraft Mod Dependencies
echo ================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python n'est pas installé ou n'est pas dans le PATH
    echo.
    echo Voulez-vous installer Python 3.11 ?
    echo.
    pause
    
    echo [*] Téléchargement de Python 3.11...
    powershell -Command "(New-Object System.Net.ServicePointManager).SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe', '%TEMP%\python_installer.exe')"
    
    if exist "%TEMP%\python_installer.exe" (
        echo [*] Installation de Python...
        "%TEMP%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1
        del "%TEMP%\python_installer.exe"
        echo [✓] Python installé avec succès
    ) else (
        echo [X] Erreur lors du téléchargement de Python
        pause
        exit /b 1
    )
) else (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [✓] Python trouvé: !PYTHON_VERSION!
)

echo.
echo [*] Mise à jour de pip...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1

echo.
echo [*] Installation des dépendances...
echo.

REM Dépendances
set "PACKAGES=flask flask-cors requests python-dotenv packaging"

for %%P in (%PACKAGES%) do (
    echo   - Installation de %%P...
    python -m pip install %%P >nul 2>&1
    if errorlevel 1 (
        echo     [X] Erreur lors de l'installation de %%P
    ) else (
        echo     [✓] %%P installé
    )
)

echo.

REM Vérifier si le fichier .env existe
if not exist ".env" (
    echo [*] Création du fichier .env...
    (
        echo # CurseForge API Configuration
        echo API_KEY=YOUR_API_KEY_HERE
        echo.
        echo # Récupérez votre clé API sur https://console.curseforge.com/
    ) > .env
    echo [✓] Fichier .env créé
    echo.
    echo [!] N'oubliez pas de configurer votre API_KEY dans le fichier .env
) else (
    echo [✓] Fichier .env existant
)

echo.
echo ================================
echo  Installation terminée !
echo ================================
echo.
echo Pour lancer l'application:
echo   python app.py
echo.
echo Accédez ensuite à: http://localhost:5000
echo.
pause
