# API de chequeo de facturas

Corre en el servidor de Profit. Solo lectura.

## Instalar
    python -m venv .venv && .venv\Scripts\activate   (Windows)
    pip install -r requirements.txt
    copy .env.example .env     # y completar

## Ejecutar
    uvicorn main:app --host 0.0.0.0 --port 8000

## Probar
    GET /salud
    GET /factura/12345      (header  X-Token: <API_TOKEN>)

Ajustar las consultas en `queries.py` al esquema real.
