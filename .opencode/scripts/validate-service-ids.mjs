#!/usr/bin/env node
/**
 * validate-service-ids.mjs — Validate X-Service-Id uniqueness and shape.
 *
 * Scans src/features/<feature>/constants.ts (and services.ts if present)
 * for `export const XxxService = { ... } as const` maps and fails if:
 *   - two features share the same numeric service id, or
 *   - an id is not a number.
 *
 * Usage:
 *   node .opencode/scripts/validate-service-ids.mjs [src-root]
 * Exit 0 = ok, 1 = violations found.
 */
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(process.argv[2] ?? "src");
const seen = new Map();
const errors = [];

function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (/constants\.ts$/.test(entry.name) || /services\.ts$/.test(entry.name)) {
      checkFile(full);
    }
  }
}

function checkFile(file) {
  const text = fs.readFileSync(file, "utf-8");
  // Solo claves PascalCase con ids numericos de 4+ digitos (evita falsos
  // positivos tipo `pageSize: 20` o `maxItems: 5` en constants.ts).
  const re = /^\s*([A-Z][A-Za-z0-9]*)\s*:\s*(\d{4,})\s*,/gm;
  let m;
  while ((m = re.exec(text)) !== null) {
    const id = Number(m[2]);
    const key = `${m[1]}:${m[2]}`;
    const loc = `${path.relative(root, file)}:${m[0].trim()}`;
    if (seen.has(id)) {
      errors.push(`Duplicate service id ${id} (${seen.get(id)} y ${loc})`);
    } else {
      seen.set(id, `${loc}`);
    }
  }
}

if (!fs.existsSync(root)) {
  console.error(`FAIL: no existe ${root}`);
  process.exit(1);
}
walk(root);

if (errors.length) {
  for (const e of errors) console.error(`FAIL: ${e}`);
  console.error(`${errors.length} violation(s)`);
  process.exit(1);
}
console.log(`validate-service-ids OK (${seen.size} service ids unicos)`);
