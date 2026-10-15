@echo off
chcp 65001 >nul
title My Darling Cat - Installer
cd /d "%~dp0"

echo ============================================
echo            My Darling Cat
echo ============================================
echo.

set "PYTHON_EXE="
set "PYTHON_CMD="

where python >nul 2>nul
if %errorlevel%==0 (
    for /f "delims=" %%i in ('where python') do (
        if not defined PYTHON_EXE set "PYTHON_EXE=%%i"
    )
)

if not defined PYTHON_EXE (
    where py >nul 2>nul
    if %errorlevel%==0 (
        set "PYTHON_CMD=py"
    )
)

if not defined PYTHON_EXE if not defined PYTHON_CMD goto install_python

if defined PYTHON_CMD (
    %PYTHON_CMD% --version >nul 2>nul
    if errorlevel 1 goto install_python
    goto check_pillow
)

"%PYTHON_EXE%" --version >nul 2>nul
if errorlevel 1 goto install_python

goto check_pillow


:install_python
echo [1/3] Python не найден. Скачиваем установщик...
echo.

set "PY_URL=https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"
set "PY_INSTALLER=%TEMP%\python_installer.exe"

powershell -NoProfile -Command "try { Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%PY_INSTALLER%' -UseBasicParsing } catch { exit 1 }"
if errorlevel 1 (
    echo.
    echo ОШИБКА: не удалось скачать Python.
    echo Проверь интернет или скачай вручную: https://www.python.org/downloads/
    pause
    exit /b 1
)

if not exist "%PY_INSTALLER%" (
    echo ОШИБКА: установщик не найден.
    pause
    exit /b 1
)

echo [2/3] Устанавливаем Python...
echo.
"%PY_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_pip=1
if errorlevel 1 (
    echo.
    echo ОШИБКА: установка Python не удалась.
    pause
    exit /b 1
)

del /F /Q "%PY_INSTALLER%" >nul 2>nul

echo Python установлен!
echo.

for /f "delims=" %%i in ('where python 2^>nul') do (
    if not defined PYTHON_EXE set "PYTHON_EXE=%%i"
)

if not defined PYTHON_EXE (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)

if not exist "%PYTHON_EXE%" (
    echo ОШИБКА: не могу найти python.exe после установки.
    echo Перезапусти этот файл.
    pause
    exit /b 1
)


:check_pillow
echo [3/3] Проверяем Pillow...
echo.

if defined PYTHON_CMD (
    %PYTHON_CMD% -c "import PIL" >nul 2>nul
    if errorlevel 1 (
        echo Устанавливаем Pillow...
        %PYTHON_CMD% -m pip install --quiet --disable-pip-version-check pillow
    )
    goto run_game
)

"%PYTHON_EXE%" -c "import PIL" >nul 2>nul
if errorlevel 1 (
    echo Устанавливаем Pillow...
    "%PYTHON_EXE%" -m pip install --quiet --disable-pip-version-check pillow
)


:run_game
echo.
echo Запускаем игру...
echo.

set "SCRIPT=%~dp0scripts\MyDarlingCat.py"

if not exist "%SCRIPT%" (
    echo ОШИБКА: не найден "%SCRIPT%"
    pause
    exit /b 1
)

if defined PYTHON_CMD (
    %PYTHON_CMD% "%SCRIPT%"
) else (
    "%PYTHON_EXE%" "%SCRIPT%"
)

exit /b 0