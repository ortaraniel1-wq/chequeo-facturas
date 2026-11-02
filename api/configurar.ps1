# Configura el usuario SQL de solo lectura y el archivo .env, sin que haya que copiar claves.
# Uso (desde la carpeta api):  powershell -ExecutionPolicy Bypass -File configurar.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$bd = "ARMOR"
$usuario = "chequeo_api"

function Azar($n) {
    $chars = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    $b = New-Object byte[] $n
    [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b)
    -join ($b | ForEach-Object { $chars[$_ % $chars.Length] })
}
function Sql($base, $consulta) {
    sqlcmd -S localhost -E -b -d $base -Q $consulta
    if ($LASTEXITCODE -ne 0) { throw "Fallo una consulta SQL (revisa el mensaje de arriba)." }
}

$clave = Azar 24
$token = Azar 40

Write-Host "1/4 Creando o actualizando el usuario SQL $usuario ..."
Sql "master" "IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name='$usuario') CREATE LOGIN $usuario WITH PASSWORD='$clave', CHECK_POLICY=OFF ELSE ALTER LOGIN $usuario WITH PASSWORD='$clave'"

Write-Host "2/4 Dando permiso de SOLO LECTURA sobre 5 tablas de $bd ..."
$grants = "factura","reng_fac","art","artbarra","clientes" | ForEach-Object { "GRANT SELECT ON dbo.$_ TO $usuario;" }
Sql $bd ("IF USER_ID('$usuario') IS NULL CREATE USER $usuario FOR LOGIN $usuario; " + ($grants -join " "))

Write-Host "3/4 Escribiendo el archivo .env ..."
$env = @(
    "SQL_SERVER=localhost",
    "SQL_DATABASE=$bd",
    "SQL_USER=$usuario",
    "SQL_PASSWORD=$clave",
    "SQL_DRIVER=ODBC Driver 17 for SQL Server",
    "API_TOKEN=$token",
    "CORS_ORIGINS="
)
Set-Content -Path ".env" -Value $env -Encoding ascii

Write-Host "4/4 Probando el acceso con el usuario nuevo ..."
sqlcmd -S localhost -U $usuario -P $clave -d $bd -b -Q "SELECT TOP 1 fact_num FROM factura"
if ($LASTEXITCODE -ne 0) { throw "El usuario nuevo no pudo entrar." }

Write-Host ""
Write-Host "LISTO. El .env quedo escrito (la clave de SQL no se muestra)."
Write-Host ""
Write-Host "TOKEN para la app (copialo al celular, NO lo compartas):"
Write-Host $token
