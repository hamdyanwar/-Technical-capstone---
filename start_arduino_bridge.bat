@echo off
chcp 65001 >nul
title MED-GUARD — Arduino Bridge

set PYTHON="C:\Users\Peter.Net\anaconda3\python.exe"

echo.
echo  ============================================
echo    MED-GUARD — Arduino Hardware Bridge
echo    الجسر البرمجي بين الأردوينو والداشبورد
echo  ============================================
echo.

REM تثبيت المتطلبات إذا لزم الأمر
echo [1/2] التحقق من المتطلبات (pyserial, requests)...
%PYTHON% -m pip install pyserial requests --quiet

echo [2/2] تشغيل جسر الأردوينو...
echo.
echo  تأكد من:
echo     1. تشغيل start_backend.bat اولا
echo     2. توصيل الاردوينو بكبل USB
echo     3. تحميل كود arduino_medguard.ino على الاردوينو
echo.
pause

cd /d "%~dp0backend"
%PYTHON% arduino_bridge.py

echo.
echo  تم ايقاف الجسر. اضغط اي زر للخروج.
pause >nul
