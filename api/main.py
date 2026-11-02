import os
import secrets
from pathlib import Path

import pyodbc
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

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
def factura(numero: int):
    try:
        with conectar() as cn:
            cur = cn.cursor()
            cur.execute(queries.ENCABEZADO, numero)
            enc = filas(cur)
            if not enc:
                raise HTTPException(status_code=404, detail="Factura no encontrada")
            cur.execute(queries.RENGLONES, numero)
            reng = filas(cur)
            cur.execute(queries.BARRAS, numero)
            barras = filas(cur)
    except pyodbc.Error:
        raise HTTPException(status_code=502, detail="Error consultando la base de datos")

    por_codigo = {}
    for b in barras:
        por_codigo.setdefault(b["codigo"], []).append(b["barra"])
    for r in reng:
        codigos = [r.get("referencia"), r.get("modelo")] + por_codigo.get(r["codigo"], [])
        vistos = []
        for c in codigos:
            c = (c or "").strip()
            if c and c not in vistos:
                vistos.append(c)
        r["barras"] = vistos
    return {"factura": enc[0], "renglones": reng}


# --- La PWA se sirve desde la misma API (mismo origen: sin CORS ni problemas de http/https) ---
# Solo estos archivos; NO se expone la carpeta del repo (api/.env, .git, etc.).
RAIZ = Path(__file__).resolve().parent.parent
PUBLICOS = {
    "": "index.html",
    "index.html": "index.html",
    "manifest.json": "manifest.json",
    "icon-192.png": "icon-192.png",
    "icon-512.png": "icon-512.png",
}


@app.get("/{archivo:path}", include_in_schema=False)
def pwa(archivo: str):
    nombre = PUBLICOS.get(archivo)
    if not nombre:
        raise HTTPException(status_code=404, detail="No encontrado")
    return FileResponse(RAIZ / nombre)
