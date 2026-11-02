"""Todas las consultas SQL viven aquí (base ARMOR de Profit Plus).

Esquema confirmado por INFORMATION_SCHEMA:
  factura(fact_num int, nombre, rif, status, fec_emis, co_cli, anulada, ...)
  reng_fac(fact_num, reng_num, co_art char(30), total_art, uni_venta, anulado, ...)
  art(co_art char(30), art_des, ref, modelo, ...)
  artbarra(codi char(20)  -- ojo: se une con art.co_art, barra char(20), des)

Los campos char vienen rellenos con espacios: se usa RTRIM.
Los alias de salida son el contrato con la app; no cambiarlos.
"""

# Encabezado. Parámetro: número de factura (int).
ENCABEZADO = """
SELECT TOP 1
    f.fact_num          AS numero,
    f.fec_emis          AS fecha,
    RTRIM(f.co_cli)     AS cliente_codigo,
    RTRIM(f.nombre)     AS cliente_nombre,
    f.status            AS status,
    f.anulada           AS anulada
FROM factura f
WHERE f.fact_num = ?
"""

# Renglones (no anulados). Parámetro: número de factura.
RENGLONES = """
SELECT
    r.reng_num                  AS renglon,
    RTRIM(r.co_art)             AS codigo,
    RTRIM(a.art_des)            AS descripcion,
    RTRIM(a.ref)                AS referencia,
    r.total_art                 AS cantidad,
    RTRIM(r.uni_venta)          AS unidad
FROM reng_fac r
LEFT JOIN art a ON a.co_art = r.co_art
WHERE r.fact_num = ?
  AND ISNULL(r.anulado, 0) = 0
ORDER BY r.reng_num
"""

# Códigos de barras de los artículos de la factura (un artículo puede tener varios).
BARRAS = """
SELECT RTRIM(b.codi) AS codigo, RTRIM(b.barra) AS barra
FROM artbarra b
WHERE b.codi IN (SELECT r.co_art FROM reng_fac r WHERE r.fact_num = ?)
"""
