# update-framework.ps1 - Sincroniza el Framework Agentico a un proyecto.
#
# Copia los artefactos del framework desde el repo raiz (Source) al proyecto
# (ProjectDir), con backup previo y validacion post-copia (validators 15).
#
# Lo que SINCRONIZA (se sobrescribe en el proyecto):
#   .opencode/framework/*   .opencode/validators/*   .opencode/agents/*
#   .opencode/scaffold/*    .opencode/scripts/*      .opencode/docs/*
#   .opencode/skills/*      (MERGE: las skills del framework se actualizan;
#                            las skills LOCALES del proyecto se conservan)
#   .opencode/mcp-metadata.json  .opencode/AGENT-ONBOARDING.md  .gitignore
#   AGENTS.md   VERSIONS.md
#
# Lo que PRESERVA (no se toca):
#   .workflow/  docs/ del proyecto  .env  opencode.json (config local; solo se
#   inyecta la instruccion de onboarding)
#
# .env.example: MERGE — la seccion del framework va ENCIMA, el contenido local
# del proyecto se conserva debajo (idempotente, no se duplica en re-syncs).
#
# Uso:
#   powershell -File update-framework.ps1 -Source "C:\ruta\ai-software-development-framework-"
#   powershell -File update-framework.ps1 -Source "..." -ProjectDir "C:\ruta\proyecto" -IncludeConfig
#   powershell -File update-framework.ps1 -Source "..." -ProjectDir "..." -PreserveLocalSkills
#
#   -IncludeConfig: copia opencode.json de la fuente SOLO si el proyecto no tiene uno.
#   -PreserveLocalSkills: ante colision de nombres, gana la skill local del proyecto.

param(
    [string]$Source = "",
    [string]$ProjectDir = "",
    [switch]$IncludeConfig,
    [switch]$PreserveLocalSkills
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

# -- Guard anti self-sync -----------------------------------------------------
# Nunca ejecutar sobre el repo fuente del framework. El default de ProjectDir
# (ubicacion del script) es exactamente ese caso: el Remove-Item del sync
# destruiria el .opencode/ del repo fuente.
if ((Resolve-Path $Source).Path -eq (Resolve-Path $ProjectDir).Path) {
    Write-Host "ERROR: Source y ProjectDir son el mismo directorio (self-sync detectado)." -ForegroundColor Red
    Write-Host "Este script sincroniza el framework HACIA un proyecto. Ejecutarlo sobre el repo fuente destruiria su .opencode/." -ForegroundColor Red
    exit 1
}

$fwSource = Join-Path $Source ".opencode"
$fwProject = Join-Path $ProjectDir ".opencode"

if (-not (Test-Path (Join-Path $Source "VERSIONS.md")) -or -not (Test-Path $fwSource)) {
    Write-Host "ERROR: '$Source' no parece el repo raiz del framework (falta VERSIONS.md/.opencode)" -ForegroundColor Red
    exit 1
}

# Modo BOOTSTRAP: el proyecto no tiene .opencode/ -> instalacion desde cero
# (sin backup: no hay nada que respaldar). El mismo script sirve para
# instalar (proyecto nuevo) y actualizar (proyecto existente).
$bootstrap = -not (Test-Path $fwProject)
if ($bootstrap) {
    Write-Host "Proyecto sin .opencode/ — modo BOOTSTRAP (instalacion desde cero)" -ForegroundColor Cyan
    New-Item -ItemType Directory -Path $fwProject -Force | Out-Null
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
if ($bootstrap) {
    $backupDir = "N/A (bootstrap)"
} else {
    Write-Host "Backup del .opencode actual en: $backupDir"
    Copy-Item -Path $fwProject -Destination $backupDir -Recurse -Force
}

# -- Sincronizar artefactos del framework -------------------------------------
$artifacts = @("framework", "validators", "agents", "scaffold", "scripts", "docs")
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

# -- Skills: MERGE (nunca borrar skills locales del proyecto) -----------------
# Las skills del framework se copian/sobrescriben; las locales del proyecto
# (no presentes en el repo) se conservan. Con -PreserveLocalSkills, ante una
# colision de nombres gana la skill local (no se sobrescribe).
$srcSkills = Join-Path $fwSource "skills"
$dstSkills = Join-Path $fwProject "skills"
New-Item -ItemType Directory -Path $dstSkills -Force | Out-Null
$keptLocal = @()
foreach ($skillDir in Get-ChildItem $srcSkills -Directory) {
    $dst = Join-Path $dstSkills $skillDir.Name
    if ((Test-Path $dst) -and $PreserveLocalSkills) {
        $keptLocal += $skillDir.Name
        Write-Host "  skill local preservada (colision): $($skillDir.Name)" -ForegroundColor Yellow
        continue
    }
    if (Test-Path $dst) { Remove-Item -LiteralPath $dst -Recurse -Force }
    Copy-Item -Path $skillDir.FullName -Destination $dst -Recurse -Force
}
$localOnly = @(Get-ChildItem $dstSkills -Directory | Where-Object { -not (Test-Path (Join-Path $srcSkills $_.Name)) })
if ($localOnly.Count -gt 0) {
    Write-Host "  skills locales del proyecto conservadas: $($localOnly.Name -join ', ')" -ForegroundColor Yellow
}
$copied += (Get-ChildItem $srcSkills -Directory | Measure-Object).Count

foreach ($rootFile in @("mcp-metadata.json", ".gitignore", "AGENT-ONBOARDING.md")) {
    $srcFile = Join-Path $fwSource $rootFile
    if (Test-Path $srcFile) {
        if ($rootFile -eq ".gitignore") {
            $giDst = Join-Path $fwProject $rootFile
            if ((Test-Path $giDst) -and -not $bootstrap) {
                $srcGI = [System.IO.File]::ReadAllText($srcFile)
                $dstGI = [System.IO.File]::ReadAllText($giDst)
                if ($srcGI -ne $dstGI) {
                    Write-Host "  ATENCION: el .gitignore del proyecto difiere del framework y sera sobrescrito." -ForegroundColor Yellow
                    Write-Host "  Si tenia personalizaciones locales, restaurarlas desde el backup ($backupDir)." -ForegroundColor Yellow
                }
            }
        }
        Copy-Item -Path $srcFile -Destination (Join-Path $fwProject $rootFile) -Force
        Write-Host "  sync .opencode/$rootFile"
    }
}

foreach ($rootFile in @("AGENTS.md", "VERSIONS.md")) {
    $srcFile = Join-Path $Source $rootFile
    if (Test-Path $srcFile) {
        Copy-Item -Path $srcFile -Destination (Join-Path $ProjectDir $rootFile) -Force
        Write-Host "  sync $rootFile"
    }
}

# -- Limpieza post-copia: nunca sincronizar entornos virtuales ni caches -------
# El .venv del source trae rutas absolutas del autor (venv roto en el destino);
# el del proyecto se borraba con el sync. Se excluyen siempre ambos lados.
Get-ChildItem -Path $fwProject -Directory -Recurse -Force |
    Where-Object { $_.Name -in @('.venv', '__pycache__') } |
    ForEach-Object {
        Remove-Item -LiteralPath $_.FullName -Recurse -Force
        Write-Host "  (excluido $($_.FullName.Replace($ProjectDir, '.')))" -ForegroundColor DarkGray
    }
if (-not (Test-Path (Join-Path $fwProject "validators\.venv"))) {
    Write-Host "  (entornos virtuales y caches no se sincronizan; para validators locales: correr .opencode\validators\setup-venv.ps1)" -ForegroundColor DarkGray
}

# .env.example: MERGE — la seccion del framework va ENCIMA y el contenido
# local del proyecto se conserva debajo (sus vars de negocio: DB, JWT, SMTP,
# integraciones...). Idempotente: si el archivo ya tiene la seccion del
# framework, no se duplica.
$envExampleDst = Join-Path $ProjectDir ".env.example"
$envExampleSrc = Join-Path $Source ".env.example"
$fwEnvMarker = "Environment Variables Template"
if (-not (Test-Path $envExampleDst)) {
    Copy-Item -Path $envExampleSrc -Destination $envExampleDst -Force
    Write-Host "  sync .env.example (no existia)"
} elseif (-not $bootstrap) {
    $localContent = [System.IO.File]::ReadAllText($envExampleDst)
    if ($localContent -match [regex]::Escape($fwEnvMarker)) {
        Write-Host "  .env.example ya contiene la seccion del framework (idempotente)" -ForegroundColor DarkGray
    } else {
        $fwContent = [System.IO.File]::ReadAllText($envExampleSrc).TrimEnd("`r", "`n")
        $sep = "# ============================================================================="
        $merged = $fwContent + "`n`n" + $sep + "`n" + "# SECCION DEL PROYECTO (env example original, preservado por el sync)" + "`n" + $sep + "`n" + $localContent
        $merged = $merged -replace "`n", "`r`n"
        [System.IO.File]::WriteAllText($envExampleDst, $merged, (New-Object System.Text.UTF8Encoding($false)))
        Write-Host "  .env.example: seccion del framework agregada ENCIMA del contenido local (preservado)" -ForegroundColor Green
    }
}

if ($IncludeConfig -or $bootstrap) {
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
