# rename-skill.ps1 — Renombra un skill en todo el framework
#
# Uso: .\rename-skill.ps1 <old-name> <new-name>
#
# Automatiza:
#   1. Renombrar carpeta skills\<old>\ -> skills\<new>\
#   2. Actualizar frontmatter name: en SKILL.md
#   3. Agregar entrada en SKILL-ALIASES.json
#   4. Buscar y reemplazar en todos los .md bajo .opencode\ + AGENTS.md + README.md
#   5. Ejecutar validadores al final

param(
    [Parameter(Mandatory=$true)]
    [string]$OldName,
    
    [Parameter(Mandatory=$true)]
    [string]$NewName
)

$ErrorActionPreference = "Stop"

$OpenCodeDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$SkillsDir = Join-Path $OpenCodeDir "skills"
$AliasesFile = Join-Path $OpenCodeDir "framework\SKILL-ALIASES.json"

# Validate name format
$namePattern = '^[a-z][a-z0-9]*(-[a-z0-9]+)+$'
if (-not ($OldName -match $namePattern)) {
    Write-Host "ERROR: '$OldName' no es un nombre de skill valido" -ForegroundColor Red
    exit 1
}
if (-not ($NewName -match $namePattern)) {
    Write-Host "ERROR: '$NewName' no es un nombre de skill valido" -ForegroundColor Red
    exit 1
}

# Validate old exists
$OldDir = Join-Path $SkillsDir $OldName
if (-not (Test-Path $OldDir)) {
    Write-Host "ERROR: skill '$OldName' no existe en $SkillsDir" -ForegroundColor Red
    exit 1
}

# Validate new does NOT exist
$NewDir = Join-Path $SkillsDir $NewName
if (Test-Path $NewDir) {
    Write-Host "ERROR: skill '$NewName' ya existe en $SkillsDir" -ForegroundColor Red
    exit 1
}

Write-Host "=== Renombrando skill: $OldName -> $NewName ==="
Write-Host ""

# 1. Rename folder
Write-Host "-> Renombrando carpeta..."
$gitDir = Join-Path $OpenCodeDir ".git"
if (Test-Path $gitDir) {
    git -C $OpenCodeDir mv $OldDir $NewDir
} else {
    Rename-Item -Path $OldDir -NewName $NewName
}

# 2. Update frontmatter name in SKILL.md
$SkillMd = Join-Path $NewDir "SKILL.md"
if (Test-Path $SkillMd) {
    Write-Host "-> Actualizando frontmatter name: en $NewName\SKILL.md..."
    $content = Get-Content $SkillMd -Raw
    $content = $content -replace "^name: $OldName$", "name: $NewName"
    Set-Content -Path $SkillMd -Value $content -NoNewline
}

# 3. Add entry in SKILL-ALIASES.json
if (Test-Path $AliasesFile) {
    $existing = Get-Content $AliasesFile -Raw | ConvertFrom-Json
    if (-not ($existing.PSObject.Properties.Name -contains $OldName)) {
        Write-Host "-> Agregando alias '$OldName' -> '$NewName' en SKILL-ALIASES.json..."
        $date = Get-Date -Format "yyyy-MM-dd"
        $entry = @{
            $OldName = @{
                current = $NewName
                deprecated_since = $date
                reason = "Renombrado automaticamente"
            }
        }
        $existing | Add-Member -NotePropertyName $OldName -NotePropertyValue $entry.$OldName -Force
        $existing | ConvertTo-Json -Depth 10 | Set-Content $AliasesFile
    } else {
        Write-Host "-> Alias '$OldName' ya existe en SKILL-ALIASES.json, saltando..."
    }
}

# 4. Find and replace in all .md files
Write-Host "-> Buscando y reemplazando '$OldName' por '$NewName' en archivos .md..."
$filesModified = 0

$mdFiles = Get-ChildItem -Path $OpenCodeDir -Filter "*.md" -Recurse -File |
    Where-Object { $_.FullName -notmatch "node_modules" -and $_.FullName -notmatch "\.venv" }

foreach ($file in $mdFiles) {
    $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
    if ($null -eq $content) { continue }
    
    $count = ([regex]::Matches($content, [regex]::Escape($OldName))).Count
    if ($count -gt 0) {
        $newContent = $content -replace "/$OldName/", "/$NewName/"
        $newContent = $newContent -replace "`$OldName`$", "`$NewName`$"
        $newContent = $newContent -replace "- $OldName", "- $NewName"
        Set-Content -Path $file.FullName -Value $newContent -NoNewline
        $filesModified++
        Write-Host "  modificado: $($file.FullName) ($count ocurrencias)"
    }
}

# Also update AGENTS.md and README.md in repo root
$repoRoot = Split-Path -Parent $OpenCodeDir
foreach ($extra in @((Join-Path $repoRoot "AGENTS.md"), (Join-Path $repoRoot "README.md"))) {
    if (Test-Path $extra) {
        $content = Get-Content $extra -Raw
        $count = ([regex]::Matches($content, [regex]::Escape($OldName))).Count
        if ($count -gt 0) {
            $newContent = $content -replace "`$OldName`$", "`$NewName`$"
            $newContent = $newContent -replace "- $OldName", "- $NewName"
            Set-Content -Path $extra -Value $newContent -NoNewline
            $filesModified++
            Write-Host "  modificado: $extra ($count ocurrencias)"
        }
    }
}

Write-Host ""
Write-Host "-> Archivos modificados: $filesModified"
Write-Host ""

# 5. Run validators
Write-Host "=== Ejecutando validadores ==="
Set-Location $OpenCodeDir

$validatorScript = Join-Path $ScriptDir "run-all.ps1"
if (Test-Path $validatorScript) {
    & powershell -File $validatorScript
    $result = $LASTEXITCODE
} else {
    python (Join-Path $OpenCodeDir "validators\check-dependencies.py")
    python (Join-Path $OpenCodeDir "validators\check-skill-contract.py")
    Write-Host "OK Validadores individuales ejecutados"
    $result = 0
}

Write-Host ""
Write-Host "=== FINALIZADO ==="
if ($result -eq 0) {
    Write-Host "OK Todos los validadores pasaron. Renombre exitoso." -ForegroundColor Green
} else {
    Write-Host "AVISO Algunos validadores fallaron. Revisa los mensajes arriba." -ForegroundColor Yellow
    Write-Host "   Puedes revertir con: git checkout -- .opencode\"
}

Write-Host ""
Write-Host "Resumen:"
Write-Host "  Skill: $OldName -> $NewName"
Write-Host "  Directorio: skills\$OldName\ -> skills\$NewName\"
Write-Host "  Archivos modificados: $filesModified"
Write-Host "  SKILL-ALIASES.json: actualizado"
