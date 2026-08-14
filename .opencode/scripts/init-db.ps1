# init-db.ps1 — Wait until PostgreSQL is ready, then create the app database
# if it does not exist. Intended for the postgres container entrypoint or for
# local dev bootstrap (docker-compose).
#
# Usage:
#   .opencode/scripts/init-db.ps1 [host] [port] [db] [user] [password]

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$PgHost = "postgres",

    [Parameter(Position = 1)]
    [string]$PgPort = "5432",

    [Parameter(Position = 2)]
    [string]$PgDb = "app",

    [Parameter(Position = 3)]
    [string]$PgUser = "postgres",

    [Parameter(Position = 4)]
    [string]$PgPassword = "postgres"
)

$ErrorActionPreference = "Stop"

$env:PGPASSWORD = $PgPassword

Write-Output "Esperando PostgreSQL en ${PgHost}:${PgPort}..."
while ($true) {
    $null = & pg_isready -h $PgHost -p $PgPort -U $PgUser 2>&1
    if ($LASTEXITCODE -eq 0) {
        break
    }
    Write-Output "  postgres aun no esta listo, reintentando en 2s..."
    Start-Sleep -Seconds 2
}
Write-Output "PostgreSQL listo."

$checkQuery = "SELECT 1 FROM pg_database WHERE datname = '$PgDb'"
$checkResult = & psql -h $PgHost -p $PgPort -U $PgUser -d postgres -tAc $checkQuery 2>&1
$dbExists = ($LASTEXITCODE -eq 0) -and ($checkResult -match '1')

if (-not $dbExists) {
    Write-Output "Creando base de datos '$PgDb'..."
    & psql -h $PgHost -p $PgPort -U $PgUser -d postgres -c "CREATE DATABASE \`"$PgDb\`";"
    if ($LASTEXITCODE -ne 0) {
        [Console]::Error.WriteLine("error: fallo al crear la base de datos '$PgDb'")
        exit $LASTEXITCODE
    }
}
Write-Output "OK: base '$PgDb' disponible."
