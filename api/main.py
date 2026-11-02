import os
import secrets

import pyodbc
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import queries

load_dotenv()

app = FastAPI(title="Chequeo de facturas API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()],
    allow_methods=["GET"],
    allow_headers=["X-Token"],
)


def verificar_token(x_token: str = Header(default="")):
    esperado = os.getenv("API_TOKEN", "")
    if not esperado or not secrets.compare_digest(x_token, esperado):
        raise HTTPException(status_code=401, detail="Token inválido")


def conectar():
    cadena = (
        f"DRIVER={{{os.getenv('SQL_DRIVER', 'ODBC Driver 17 for SQL Server')}}};"
        f"SERVER={os.getenv('SQL_SERVER')};DATABASE={os.getenv('SQL_DATABASE')};"
        f"UID={os.getenv('SQL_USER')};PWD={os.getenv('SQL_PASSWORD')};"
        "ApplicationIntent=ReadOnly;TrustServerCertificate=yes"
    )
    return pyodbc.connect(cadena, timeout=10)


def filas(cursor):
    cols = [c[0] for c in cursor.description]
    return [dict(zip(cols, r)) for r in cursor.fetchall()]


@app.get("/salud")
def salud():
    return {"ok": True}


@app.get("/factura/{numero}", dependencies=[Depends(verificar_token)])
def factura(numero: str):
    try:
        with conectar() as cn:
            cur = cn.cursor()
            cur.execute(queries.ENCABEZADO, numero)
            enc = filas(cur)
            if not enc:
                raise HTTPException(status_code=404, detail="Factura no encontrada")
            cur.execute(queries.RENGLONES, numero)
            reng = filas(cur)
    except pyodbc.Error:
        raise HTTPException(status_code=502, detail="Error consultando la base de datos")
    return {"factura": enc[0], "renglones": reng}
