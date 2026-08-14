# update-framework.ps1 - Sincroniza el Framework Agentico a un proyecto.
#
# Copia los artefactos del framework desde el repo raiz (Source) al proyecto
# (ProjectDir), con backup previo y validacion post-copia (validators 15).
#
# Lo que SINCRONIZA (se sobrescribe en el proyecto):
#   .opencode/framework/*   .opencode/skills/*   .opencode/validators/*
#   .opencode/agents/*      .opencode/scaffold/* .opencode/scripts/*
#   .opencode/docs/*        AGENTS.md            .env.example
#
# Lo que PRESERVA (no se toca):
#   .workflow/  docs/ del proyecto  .env  opencode.json (config local del proyecto)
#
# Uso:
#   powershell -File update-framework.ps1 -Source "C:\ruta\ai-software-development-framework-"
#   powershell -File update-framework.ps1 -Source "..." -ProjectDir "C:\ruta\proyecto" -IncludeConfig
#
#   -IncludeConfig: copia opencode.json de la fuente SOLO si el proyecto no tiene uno.

param(
    [string]$Source = "",
    [string]$ProjectDir = "",
    [switch]$IncludeConfig
)

$ErrorActionPreference = "Stop"

# -- Resolucion de rutas ------------------------------------------------------
if (-not $ProjectDir) {
    $ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path  # .opencode/scripts/
    $ProjectDir = Split-Path -Parent $ProjectDir                    # .opencode/
    $ProjectDir = Split-Path -Parent $ProjectDir                    # raiz del proyecto
}
if (-not $Source) {
    $Source = Read-Host "Ruta del repo raiz del framework (con .opencode/)"
}
$Source = (Resolve-Path $Source).Path
$ProjectDir = (Resolve-Path $ProjectDir).Path

$fwSource = Join-Path $Source ".opencode"
$fwProject = Join-Path $ProjectDir ".opencode"

if (-not (Test-Path (Join-Path $Source "VERSIONS.md")) -or -not (Test-Path $fwSource)) {
    Write-Host "ERROR: '$Source' no parece el repo raiz del framework (falta VERSIONS.md/.opencode)" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $fwProject)) {
    Write-Host "ERROR: '$ProjectDir' no tiene .opencode/ - es un proyecto con el framework instalado?" -ForegroundColor Red
    exit 1
}

# -- Versiones ----------------------------------------------------------------
function Get-Version([string]$dir) {
    $v = Join-Path $dir "VERSIONS.md"
    if (-not (Test-Path $v)) { return "desconocida" }
    $line = Select-String -Path $v -Pattern "^\| 4\.\d+\.\d+" | Select-Object -First 1
    if (-not $line) { return "desconocida" }
    return ($line.Line -split "\|")[1].Trim()
}

$srcVer = Get-Version $Source
$projVer = Get-Version $ProjectDir

Write-Host ""
Write-Host "Framework: $projVer -> $srcVer" -ForegroundColor Cyan
if ($projVer -eq $srcVer) {
    Write-Host "El proyecto ya tiene la version $srcVer. Continuando igual (Ctrl+C para cancelar)..." -ForegroundColor Yellow
}

# -- Backup -------------------------------------------------------------------
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = Join-Path $ProjectDir ".opencode-backup-$stamp"
Write-Host "Backup del .opencode actual en: $backupDir"
Copy-Item -Path $fwProject -Destination $backupDir -Recurse -Force

# -- Sincronizar artefactos del framework -------------------------------------
$artifacts = @("framework", "skills", "validators", "agents", "scaffold", "scripts", "docs")
$copied = 0
foreach ($art in $artifacts) {
    $srcArt = Join-Path $fwSource $art
    if (-not (Test-Path $srcArt)) { continue }
    $dstArt = Join-Path $fwProject $art
    if (Test-Path $dstArt) { Remove-Item -LiteralPath $dstArt -Recurse -Force }
    Copy-Item -Path $srcArt -Destination $dstArt -Recurse -Force
    $copied++
    Write-Host "  sync .opencode/$art"
}

foreach ($rootFile in @("mcp-metadata.json", ".gitignore", "AGENT-ONBOARDING.md")) {
    $srcFile = Join-Path $fwSource $rootFile
    if (Test-Path $srcFile) {
        Copy-Item -Path $srcFile -Destination (Join-Path $fwProject $rootFile) -Force
        Write-Host "  sync .opencode/$rootFile"
    }
}

foreach ($rootFile in @("AGENTS.md", ".env.example", "VERSIONS.md")) {
    $srcFile = Join-Path $Source $rootFile
    if (Test-Path $srcFile) {
        Copy-Item -Path $srcFile -Destination (Join-Path $ProjectDir $rootFile) -Force
        Write-Host "  sync $rootFile"
    }
}

if ($IncludeConfig) {
    $ocSrc = Join-Path $Source "opencode.json"
    $ocDst = Join-Path $ProjectDir "opencode.json"
    if (Test-Path $ocSrc) {
        if (-not (Test-Path $ocDst)) {
            Copy-Item -Path $ocSrc -Destination $ocDst -Force
            Write-Host "  sync opencode.json (el proyecto no tenia uno)"
        } else {
            Write-Host "  opencode.json NO se sobrescribio (config local del proyecto)" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  opencode.json NO se toco (usa -IncludeConfig para sincronizarlo)" -ForegroundColor DarkGray
}

# -- Inyeccion de la instruccion de onboarding en opencode.json del proyecto --
# (solo si el proyecto tiene uno; preserva el resto de su config)
$ocProj = Join-Path $ProjectDir "opencode.json"
if (Test-Path $ocProj) {
    try {
        $cfg = Get-Content $ocProj -Raw | ConvertFrom-Json
        $instr = @($cfg.instructions)
        if ($instr -notcontains ".opencode/AGENT-ONBOARDING.md") {
            $cfg.instructions = @($instr + ".opencode/AGENT-ONBOARDING.md")
            $json = $cfg | ConvertTo-Json -Depth 12
            [System.IO.File]::WriteAllText($ocProj, $json, (New-Object System.Text.UTF8Encoding($false)))
            Write-Host "  opencode.json: instruccion AGENT-ONBOARDING.md inyectada (autoconfiguracion)" -ForegroundColor Green
        } else {
            Write-Host "  opencode.json: ya tiene AGENT-ONBOARDING.md" -ForegroundColor DarkGray
        }
    } catch {
        Write-Host "  opencode.json: no se pudo inyectar la instruccion (JSON invalido?) - revisar manualmente" -ForegroundColor Yellow
    }
}

# -- Validacion post-copia ----------------------------------------------------
Write-Host ""
Write-Host "Ejecutando validators del framework..." -ForegroundColor Cyan
$runAll = Join-Path $fwProject "validators\run-all.ps1"
$venvPy = Join-Path $fwProject "validators\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    $setup = Join-Path $fwProject "validators\setup-venv.ps1"
    if (Test-Path $setup) { & $setup | Out-Null }
}
if (Test-Path $runAll) {
    # El run-all escribe WARNs/FAILs a stderr; con Stop esos NativeCommandError
    # abortarian el script. Se corre en modo Continue y se evalua por exit code.
    $prevEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & $runAll
    $ErrorActionPreference = $prevEAP
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ATENCION: los validators fallaron tras la copia. Revisar antes de seguir." -ForegroundColor Yellow
    }
} else {
    Write-Host "  (run-all.ps1 no encontrado en el proyecto)" -ForegroundColor DarkGray
}

# -- Registro de version instalada --------------------------------------------
$wfDir = Join-Path $ProjectDir ".workflow"
if (-not (Test-Path $wfDir)) { New-Item -ItemType Directory -Path $wfDir -Force | Out-Null }
Set-Content -Path (Join-Path $wfDir "framework-version.txt") -Value "$srcVer`nSincronizado: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`nDesde: $Source" -Encoding UTF8

Write-Host ""
Write-Host "Framework actualizado: $projVer -> $srcVer ($($copied) artefactos sincronizados)" -ForegroundColor Green
Write-Host "Backup disponible en: $backupDir"
Write-Host "Reinicia opencode para cargar las skills/framework actualizados." -ForegroundColor Cyan
