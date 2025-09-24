@echo off
title Limitless Bulk Import Tool

echo ========================================
echo     LIMITLESS BULK IMPORT TOOL
echo ========================================
echo.

REM Check for .env file
if not exist .env (
    echo ERROR: .env file not found!
    echo Please create .env from .env.template first
    pause
    exit /b 1
)

REM Load environment variables from .env
for /f "delims=" %%x in (.env) do (
    set "%%x"
)

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

:menu
echo Select an import option:
echo.
echo 1) Import LAST 30 DAYS
echo 2) Import LAST 90 DAYS  
echo 3) Import LAST 365 DAYS (Full Year)
echo 4) Import ALL AVAILABLE DATA
echo 5) Import CUSTOM DATE RANGE
echo 6) Retry FAILED imports
echo 7) Quick import (Last 7 days)
echo 8) Exit
echo.
set /p choice=Enter choice [1-8]: 

if "%choice%"=="1" goto days30
if "%choice%"=="2" goto days90
if "%choice%"=="3" goto days365
if "%choice%"=="4" goto all
if "%choice%"=="5" goto custom
if "%choice%"=="6" goto retry
if "%choice%"=="7" goto quick
if "%choice%"=="8" goto end

echo Invalid choice. Please try again.
echo.
goto menu

:days30
echo.
echo Importing last 30 days...
python bulk_import_limitless.py --days-back 30
goto done

:days90
echo.
echo Importing last 90 days...
python bulk_import_limitless.py --days-back 90
goto done

:days365
echo.
echo Importing last 365 days...
python bulk_import_limitless.py --days-back 365
goto done

:all
echo.
echo Importing all available data...
echo This may take a while depending on how much data you have.
set /p confirm=Continue? (y/n): 
if /i "%confirm%"=="y" (
    python bulk_import_limitless.py
)
goto done

:custom
echo.
set /p start_date=Enter start date (YYYY-MM-DD): 
set /p end_date=Enter end date (YYYY-MM-DD) or press Enter for today: 
if "%end_date%"=="" (
    python bulk_import_limitless.py --start-date %start_date%
) else (
    python bulk_import_limitless.py --start-date %start_date% --end-date %end_date%
)
goto done

:retry
echo.
echo Retrying failed imports...
python bulk_import_limitless.py --retry-failed
goto done

:quick
echo.
echo Quick import - last 7 days...
python bulk_import_limitless.py --days-back 7 --workers 1
goto done

:done
echo.
echo ========================================
echo Import process complete!
echo Check your GitHub repository for the imported notes.
echo ========================================
echo.
pause
goto menu

:end
exit /b 0
