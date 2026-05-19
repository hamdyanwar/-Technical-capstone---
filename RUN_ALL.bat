@echo off
title MED-GUARD UNIFIED LAUNCHER
color 0A
echo =======================================================
echo          MED-GUARD SYSTEM LAUNCHER (ALL-IN-ONE)
echo             تشغيل النظام بالكامل بضغطة واحدة
echo =======================================================
echo.

:: 1. تنظيف أي عمليات بايثون قديمة معلقة لتفادي تعليق المنافذ
echo [*] Cleaning up old background tasks...
taskkill /f /im python.exe >nul 2>&1
timeout /t 1 /nobreak >nul

:: 2. التأكد من إصلاح مكتبة numpy وتثبيت مكتبات الأردوينو
echo [*] Ensuring correct library versions (Numpy ^& Serial)...
"C:\Users\Peter.Net\anaconda3\python.exe" -m pip install "numpy<2" "pyserial" "requests" --quiet

:: 3. تشغيل الباكند في شاشة خلفية
echo [*] Launching Backend Server...
cd /d "%~dp0backend"
start "Med-Guard Backend" /min "C:\Users\Peter.Net\anaconda3\python.exe" -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

:: 4. الانتظار ليتأكد من عمل الباكند بالكامل
echo [*] Waiting for Backend to initialize (4 seconds)...
timeout /t 4 /nobreak >nul

:: 5. فتح صفحة السوفتوير في المتصفح تلقائياً
echo [*] Opening Dashboard...
start "" "%~dp0frontend\index.html"

:: 6. تشغيل الجسر البرمجي لربط الأردوينو تلقائياً
echo [*] Connecting to Arduino & Starting Bridge...
echo -------------------------------------------------------
"C:\Users\Peter.Net\anaconda3\python.exe" link_hardware.py

pause
