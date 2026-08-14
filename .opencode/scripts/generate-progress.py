#!/usr/bin/env python3
"""generate-progress.py — Genera el dashboard de progreso (artifact HTML).

Lee las fuentes del proyecto y produce un HTML autocontenido (sin dependencias)
con:
  1. Vista principal por MODULOS de negocio (lo que ve el supervisor): cada
     modulo de docs/api-first/*.md con semaforo, % de tareas, fecha,
     responsable y link a la spec.
  2. Panel por FASES del framework N0-N49 (dev/IA): tabla A-H con estado.
  3. Panel "donde quedo la IA": ultimo checkpoint y proximos pasos.

Fuentes:
  - docs/api-first/*.md            -> modulos y specs
  - .workflow/state.json           -> pasos completados/fallidos/actual
  - tasks.md (raiz)                -> tareas por modulo (checkboxes)
  - docs/artifacts/progress-state.json -> override manual opcional
        {"modulo": {"status": "ok|wip|blocked|pending", "fecha": "..",
                     "responsable": "..", "notas": ".."}}

Uso:
  python .opencode/scripts/generate-progress.py [project-dir]
Salida: <project-dir>/docs/artifacts/progress.html
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

PROJECT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()

STATUS_META = {
    "ok": ("OK", "#1a7f37", "🟢"),
    "wip": ("EN CURSO", "#9a6700", "🔄"),
    "blocked": ("BLOQUEADO", "#cf222e", "🚫"),
    "pending": ("PENDIENTE", "#57606a", "⏳"),
}


def read_json(p: Path):
    if p.exists():
        try:
            # utf-8-sig tolera el BOM que PowerShell anade al escribir JSON
            return json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:
            return {}
    return {}


# ── 1. Modulos (specs) ───────────────────────────────────────────────────────
api_dir = PROJECT / "docs" / "api-first"
modules = []
if api_dir.exists():
    for spec in sorted(api_dir.glob("*.md")):
        if spec.name.lower() == "readme.md":
            continue  # el indice de la carpeta no es un modulo
        text = spec.read_text(encoding="utf-8", errors="replace")
        title = spec.stem.replace("-", " ").title()
        m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        if m:
            title = m.group(1).strip()
        endpoints = len(re.findall(r"^\|\s*(?:GET|POST|PUT|DELETE|PATCH)\s*\|", text, re.MULTILINE | re.IGNORECASE))
        modules.append({"slug": spec.stem, "title": title, "path": str(spec.relative_to(PROJECT)), "endpoints": endpoints})

# Modulos extra declarados en progress-state.json (sin spec formal en
# docs/api-first/): {"_extra": [{"slug": "auth", "title": "Autenticacion", "path": "..."}]}
override_early = read_json(PROJECT / "docs" / "artifacts" / "progress-state.json")
known_slugs = {m["slug"] for m in modules}
for extra in override_early.get("_extra", []):
    if extra.get("slug") and extra["slug"] not in known_slugs:
        modules.append({
            "slug": extra["slug"],
            "title": extra.get("title", extra["slug"].replace("-", " ").title()),
            "path": extra.get("path", ""),
            "endpoints": int(extra.get("endpoints", 0) or 0),
        })

# ── 2. Estado del workflow ───────────────────────────────────────────────────
state = read_json(PROJECT / ".workflow" / "state.json")
steps_done = set(state.get("steps_completed", []))
steps_failed = set(state.get("steps_failed", []))
current_step = state.get("current_step", "—")
checkpoint = state.get("last_checkpoint", state.get("started_at", "—"))

# ── 3. Tareas por modulo (tasks.md) ──────────────────────────────────────────
tasks_md = PROJECT / "tasks.md"
module_tasks = {}  # slug -> (done, total)
if tasks_md.exists():
    current_mod = None
    for line in tasks_md.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^#{1,3}\s+(.+)$", line)
        if m:
            heading = m.group(1).strip().lower()
            current_mod = None
            for mod in modules:
                if mod["slug"] in heading or heading in mod["slug"]:
                    current_mod = mod["slug"]
                    break
            continue
        t = re.match(r"^\s*[-*]\s*\[([ xX])\]\s*(.+)$", line)
        if t and current_mod:
            done, total = module_tasks.get(current_mod, (0, 0))
            module_tasks[current_mod] = (done + (1 if t.group(1).lower() == "x" else 0), total + 1)

# ── 4. Override manual (progress-state.json) ─────────────────────────────────
override = read_json(PROJECT / "docs" / "artifacts" / "progress-state.json")

# ── 5. Estado por modulo ─────────────────────────────────────────────────────
# Heuristica multi-nivel para mapear pasos del state.json a modulos:
#   a. override manual (progress-state.json) — prioridad 1
#   b. tokens de pasos tipo "SPRINT-{n}-<modulo>-..." y cualquier paso que
#      contenga el slug o palabras del titulo (normalizadas sin acentos)
import unicodedata

_STOP = {"sprint", "sprints", "bundle", "fix", "dec", "td", "ex", "n", "e2e", "test", "tests",
         "backend", "frontend", "calidad", "discovery", "revalidacion", "verificado", "navegador",
         "contrato", "security", "seguridad", "missinggreenlet", "calamine", "api", "python",
         "github", "actions", "docker", "compose", "alembic", "pytest", "eslint", "tsc", "build"}


def norm_txt(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", s.lower())


def module_tokens(mod):
    toks = set(norm_txt(mod["slug"]).split())
    for w in norm_txt(mod["title"]).split():
        if len(w) >= 3 and w not in _STOP:
            toks.add(w)
    return toks


def step_matches(step, toks):
    n = set(norm_txt(step).split())
    return bool(n & toks)


for mod in modules:
    done, total = module_tasks.get(mod["slug"], (0, 0))
    mod["tasks_done"] = done
    mod["tasks_total"] = total
    mod["pct"] = round(done / total * 100) if total else None

    ov = override.get(mod["slug"], {})
    if ov.get("status"):
        mod["status"] = ov["status"]
        mod["fecha"] = ov.get("fecha", "—")
        mod["responsable"] = ov.get("responsable", "—")
        mod["notas"] = ov.get("notas", "")
    else:
        toks = module_tokens(mod)
        hit_done = any(step_matches(d, toks) for d in steps_done)
        hit_fail = any(step_matches(f, toks) for f in steps_failed)
        hit_wip = step_matches(current_step, toks)
        if hit_fail:
            mod["status"] = "blocked"
        elif hit_wip:
            mod["status"] = "wip"
        elif hit_done:
            mod["status"] = "ok"
        elif total and done:
            mod["status"] = "wip"
        else:
            mod["status"] = "pending"
        mod["fecha"] = checkpoint
        mod["responsable"] = "—"
        mod["notas"] = ""

# ── 6. Fases del framework (N0-N49) ──────────────────────────────────────────
PHASES = [
    ("A — Gobierno", "N0-N4", ["requirements-intake", "framework-governance", "framework-discovery", "framework-conception", "hu-template"]),
    ("B — Arquitectura", "N5-N9", ["framework-architecture", "framework-core-design", "framework-pack-design", "framework-data-memory-compliance", "framework-security", "framework-platform"]),
    ("C — Scaffold", "N10-N15", ["framework-scaffold-implementation", "project-architecture", "project-bootstrap", "repo-structure", "app-bootstrap", "backend-api"]),
    ("D — Especificación", "N16", ["api-first-spec"]),
    ("E — Backend", "N17-N31", ["api-first-backend", "database-modeling", "data-access", "authentication", "authorization", "error-handling", "api-integration"]),
    ("F — Frontend", "N32-N37", ["api-first-frontend", "react", "react-services", "typescript", "design-system", "i18n"]),
    ("G — Calidad", "N38-N44", ["unit-testing", "integration-testing", "playwright", "security-testing", "code-review", "accesibilidad"]),
    ("H — Operación", "N45-N49", ["ci-cd", "observabilidad", "infrastructure-as-code", "disaster-recovery", "pull-request", "framework-operations-evolution"]),
]


def step_status(step_name):
    toks = set(norm_txt(step_name).split())
    if any(set(norm_txt(f).split()) & toks for f in steps_failed):
        return "blocked"
    if any(set(norm_txt(d).split()) & toks for d in steps_done):
        return "ok"
    if set(norm_txt(current_step).split()) & toks:
        return "wip"
    return "pending"


phase_rows = []
for name, levels, skills in PHASES:
    st = [step_status(s) for s in skills]
    done_n = st.count("ok")
    wip_n = st.count("wip")
    state_label = f"{done_n}/{len(skills)}"
    if "blocked" in st:
        badge = ("blocked", "BLOQUEADO")
    elif wip_n:
        badge = ("wip", f"EN CURSO ({wip_n})")
    elif done_n == len(skills):
        badge = ("ok", "COMPLETADA")
    else:
        badge = ("pending", "PENDIENTE")
    phase_rows.append((name, levels, state_label, badge, st))

done_total = sum(1 for s in set(steps_done))
pct_global = min(100, round(done_total / 50 * 100)) if steps_done else 0

# ── 7. Render HTML ───────────────────────────────────────────────────────────
def mod_card(m):
    label, color, icon = STATUS_META.get(m["status"], STATUS_META["pending"])
    pct_txt = f"{m['pct']}%" if m["pct"] is not None else "—"
    tasks_txt = f"{m['tasks_done']}/{m['tasks_total']}" if m["tasks_total"] else "—"
    notas = f"<p class='notas'>{m['notas']}</p>" if m.get("notas") else ""
    return f"""<div class="card {m['status']}">
    <div class="card-head">
      <span class="icon">{icon}</span>
      <h3>{m['title']}</h3>
      <span class="badge" style="color:{color};border-color:{color}">{label}</span>
    </div>
    <div class="meta">
      <span>Tareas: <b>{tasks_txt}</b></span>
      <span>Progreso: <b>{pct_txt}</b></span>
      <span>Endpoints: <b>{m['endpoints']}</b></span>
    </div>
    <div class="bar"><div class="bar-fill" style="width:{m['pct'] or 0}%"></div></div>
    <div class="meta small">
      <span>Fecha: {m.get('fecha','—')}</span>
      <span>Responsable: {m.get('responsable','—')}</span>
    </div>
    <a class="link" href="../../{m['path']}">Ver spec</a>
    {notas}
  </div>"""

phase_html = "".join(
    f"""<tr class="{badge[0]}"><td>{name}</td><td>{levels}</td><td>{state_label}</td>
        <td><span class="badge" style="color:{STATUS_META[badge[0]][1]};border-color:{STATUS_META[badge[0]][1]}">{badge[1]}</span></td>
        <td>{' '.join(s[0].upper() for s in st)}</td></tr>"""
    for name, levels, state_label, badge, st in phase_rows
)

mods_html = "\n".join(mod_card(m) for m in modules) if modules else "<p class='empty'>No hay specs en docs/api-first/ — genera las specs con la skill api-first-spec.</p>"

html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Progreso del Proyecto — {PROJECT.name}</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background:#f6f8fa; color:#1f2328; padding:24px; }}
  header {{ display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:20px; }}
  h1 {{ font-size:22px; }}
  .sub {{ color:#57606a; font-size:13px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:16px; }}
  .card {{ background:#fff; border:1px solid #d0d7de; border-radius:8px; padding:16px; display:flex; flex-direction:column; gap:10px; }}
  .card.blocked {{ border-left:4px solid #cf222e; }}
  .card.wip {{ border-left:4px solid #9a6700; }}
  .card.ok {{ border-left:4px solid #1a7f37; }}
  .card-head {{ display:flex; align-items:center; gap:8px; }}
  .card-head h3 {{ font-size:15px; flex:1; }}
  .icon {{ font-size:18px; }}
  .badge {{ border:1px solid; border-radius:20px; padding:2px 10px; font-size:11px; font-weight:600; }}
  .meta {{ display:flex; gap:14px; font-size:12px; color:#57606a; flex-wrap:wrap; }}
  .meta.small {{ font-size:11px; }}
  .bar {{ height:8px; background:#eaeef2; border-radius:4px; overflow:hidden; }}
  .bar-fill {{ height:100%; background:#1a7f37; border-radius:4px; }}
  .link {{ font-size:12px; color:#0969da; text-decoration:none; }}
  .notas {{ font-size:12px; color:#57606a; font-style:italic; }}
  h2 {{ font-size:16px; margin:28px 0 10px; }}
  table {{ width:100%; border-collapse:collapse; background:#fff; border:1px solid #d0d7de; border-radius:8px; overflow:hidden; font-size:13px; }}
  th,td {{ padding:8px 12px; text-align:left; border-bottom:1px solid #eaeef2; }}
  th {{ background:#f6f8fa; }}
  tr.blocked td {{ background:#fff5f5; }}
  tr.wip td {{ background:#fff8e6; }}
  tr.ok td {{ background:#f0fff4; }}
  .panel {{ background:#fff; border:1px solid #d0d7de; border-radius:8px; padding:14px; font-size:13px; }}
  .panel b {{ color:#1f2328; }}
  .global {{ display:flex; align-items:center; gap:12px; margin-bottom:6px; }}
  .gbar {{ flex:1; height:14px; background:#eaeef2; border-radius:7px; overflow:hidden; }}
  .gbar-fill {{ height:100%; background:linear-gradient(90deg,#1a7f37,#2da44e); }}
  .empty {{ color:#57606a; font-style:italic; }}
</style>
</head>
<body>
<header>
  <div>
    <h1>📊 Progreso — {PROJECT.name}</h1>
    <div class="sub">Generado {datetime.now().strftime('%Y-%m-%d %H:%M')} · Último checkpoint: {checkpoint}</div>
  </div>
  <div class="global">
    <b>Global:</b>
    <div class="gbar"><div class="gbar-fill" style="width:{pct_global}%"></div></div>
    <b>{pct_global}%</b>
  </div>
</header>

<h2>Módulos de negocio</h2>
<div class="grid">{mods_html}</div>

<h2>Fases del framework</h2>
<table>
  <tr><th>Fase</th><th>Niveles</th><th>Completadas</th><th>Estado</th><th>Resumen</th></tr>
  {phase_html}
</table>

<h2>¿Dónde quedó la IA?</h2>
<div class="panel">
  <p><b>Paso actual:</b> {current_step}</p>
  <p><b>Checkpoint:</b> {checkpoint}</p>
  <p><b>Pasos completados:</b> {done_total}/50</p>
  <p><b>Próximo paso:</b> consultar el estado en <code>.workflow/state.json</code> y continuar con el siguiente nivel del routing (SKILL-ROUTING.md).</p>
</div>
</body>
</html>"""

out_dir = PROJECT / "docs" / "artifacts"
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "progress.html"
out_file.write_text(html, encoding="utf-8")
print(f"OK: {out_file} ({len(html)} bytes, {len(modules)} modulos, {pct_global}% global)")
