@echo off
:: ONIX-BOT Installation Script for Windows
:: Author: Ian Carter Kulani
:: Version: 2.0.0

setlocal enabledelayedexpansion

:: Colors for Windows (using ANSI if supported)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "CYAN=[96m"
set "NC=[0m"

echo %RED%
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                      ONIX-BOT INSTALLER                          ║
echo ║                         Version 2.0.0                            ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo %NC%
echo.

:: Check Python
echo %CYAN%[*] Checking Python installation...%NC%
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[!] Python not found. Please install Python 3.7+ from python.org%NC%
    echo %YELLOW%Make sure to check "Add Python to PATH" during installation%NC%
    pause
    exit /b 1
)

for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PYTHON_VER=%%a
echo %GREEN%[✓] Python %PYTHON_VER% found%NC%

:: Check pip
echo %CYAN%[*] Checking pip...%NC%
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[!] pip not found. Installing...%NC%
    python -m ensurepip
)
echo %GREEN%[✓] pip available%NC%

:: Create virtual environment
echo %CYAN%[*] Creating virtual environment...%NC%
if exist venv (
    echo %YELLOW%[!] Virtual environment already exists%NC%
) else (
    python -m venv venv
    echo %GREEN%[✓] Virtual environment created%NC%
)

:: Activate and install dependencies
echo %CYAN%[*] Installing Python dependencies...%NC%
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo %RED%[!] Failed to install dependencies%NC%
    pause
    exit /b 1
)
echo %GREEN%[✓] Dependencies installed%NC%

:: Create directories
echo %CYAN%[*] Creating configuration directories...%NC%
if not exist ".onix\phishing" mkdir ".onix\phishing"
if not exist ".onix\captured" mkdir ".onix\captured"
if not exist "reports" mkdir "reports"
if not exist "logs" mkdir "logs"
echo %GREEN%[✓] Directories created%NC%

:: Create configuration
echo %CYAN%[*] Creating configuration file...%NC%
(
echo {
echo     "version": "2.0.0",
echo     "database": ".onix/onix.db",
echo     "log_file": "logs/onix.log",
echo     "phishing_dir": ".onix/phishing",
echo     "captured_dir": ".onix/captured",
echo     "web_port": 5000,
echo     "phish_port": 8080,
echo     "auto_start_web": true,
echo     "encryption_enabled": true,
echo     "max_log_size_mb": 100,
echo     "retention_days": 30
echo }
) > config.json
echo %GREEN%[✓] Configuration created%NC%

:: Create run script
echo %CYAN%[*] Creating run script...%NC%
(
echo @echo off
echo call venv\Scripts\activate.bat
echo python onix_bot.py
echo pause
) > run.bat
echo %GREEN%[✓] Run script created (run.bat)%NC%

:: Create PowerShell shortcut script
echo %CYAN%[*] Creating desktop shortcut...%NC%
set "SCRIPT_PATH=%cd%\run.bat"
set "SHORTCUT_PATH=%USERPROFILE%\Desktop\ONIX-BOT.lnk"

powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%SHORTCUT_PATH%'); $SC.TargetPath = '%SCRIPT_PATH%'; $SC.WorkingDirectory = '%cd%'; $SC.Save()"
echo %GREEN%[✓] Desktop shortcut created%NC%

:: Final message
echo.
echo %GREEN%════════════════════════════════════════════════════════════%NC%
echo %GREEN%✓ ONIX-BOT installation completed successfully!%NC%
echo %GREEN%════════════════════════════════════════════════════════════%NC%
echo.
echo %CYAN%To start ONIX-BOT:%NC%
echo   Double-click run.bat
echo   OR
echo   run "venv\Scripts\activate" then "python onix_bot.py"
echo.
echo %YELLOW%For help: type 'help' in the bot terminal%NC%
echo.

pause