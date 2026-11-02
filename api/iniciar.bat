@echo off
rem Arranca la API de chequeo de facturas. Se usa desde una tarea programada al iniciar Windows.
cd /d C:\chequeo-facturas\api
call .venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8000 >> C:\chequeo-facturas\api\api.log 2>&1
