@echo off
cd /d "%~dp0"
call .venv\Scripts\activate
py -m sgm.desktop.executar
if errorlevel 1 pause
