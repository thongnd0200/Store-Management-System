@echo off
chcp 65001 >nul 2>&1
echo ============================================
echo   Building Store Management System .exe
echo ============================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Installing build dependencies...
pip install pyinstaller flask --quiet

echo.
echo Building executable...
pyinstaller store.spec --noconfirm

echo.
if exist "dist\StoreManagement\StoreManagement.exe" (
    echo ============================================
    echo   Build successful!
    echo   Output: dist\StoreManagement\
    echo   Run:    dist\StoreManagement\StoreManagement.exe
    echo ============================================
) else (
    echo [ERROR] Build failed. Check errors above.
)
echo.
pause
