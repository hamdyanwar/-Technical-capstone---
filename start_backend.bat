@echo off
title Med-Guard Intelligence Layer - Backend
color 06
echo =======================================================
echo          MED-GUARD SYSTEM INTELLIGENCE LAYER
echo           ENGINEER MICHAEL - SYSTEM ADVISOR
echo =======================================================
echo.
echo [AUTH] Verifying Engineering Protocols... [cite: 1, 2]
echo [INFO] Establishing connection to Clincal Database... 

:: الانتقال لمجلد الـ backend لضمان قراءة الملفات بشكل صحيح 
cd /d "%~dp0backend"

echo [EXEC] Launching Med-Guard Core (FastAPI)... 
echo [INFO] Opening Web Interface...
start "" "%~dp0frontend\index.html"
echo.

:: تشغيل المحرك باستخدام uvicorn مع الحفاظ على المنفذ 8000 [cite: 2, 3]
"C:\Users\Peter.Net\anaconda3\python.exe" -m uvicorn main:app --reload --host 127.0.0.1 --port 8000 

:: فحص ما إذا كان هناك خطأ في التشغيل للبقاء على اطلاع بالحالة التقنية
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] System failure detected. Please verify Python environment and main.py path.
)

pause
