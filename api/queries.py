"""Todas las consultas SQL viven aquí.

TODO: ajustar nombres de tablas/columnas al esquema real de Profit Plus.
Los nombres de abajo son PLACEHOLDERS. Los alias de salida (codigo, barras,
descripcion, cantidad, ...) son los que espera la app y no deben cambiar.
"""

# Encabezado de la factura. Parámetro: número de factura.
ENCABEZADO = """
SELECT TOP 1
    f.fact_num      AS numero,
    f.fec_emis      AS fecha,
    f.co_cli        AS cliente_codigo
FROM factura f            -- TODO tabla real
WHERE f.fact_num = ?
"""

# Renglones de la factura. Parámetro: número de factura.
RENGLONES = """
SELECT
    r.reng_num      AS renglon,
    r.co_art        AS codigo,
    a.cod_bar       AS barras,        -- TODO columna real del código de barras
    a.art_des       AS descripcion,
    r.total_art     AS cantidad
FROM reng_fac r           -- TODO tabla real
JOIN art a ON a.co_art = r.co_art
WHERE r.fact_num = ?
ORDER BY r.reng_num
"""
