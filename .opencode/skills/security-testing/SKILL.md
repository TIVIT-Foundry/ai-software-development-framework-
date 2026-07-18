---
name: security-testing
description: "Security testing and vulnerability scanning patterns. Covers SAST (SonarQube/Semgrep), DAST (OWASP ZAP), dependency scanning (bun audit, pip-audit, Dependabot, Snyk), secret scanning, OAuth2/Keycloak auth testing, security gates in CI, and vulnerability reporting. Trigger: When implementing security testing, configuring SAST/DAST in pipelines, or performing security audits."
version: 1.0
metadata:
  phase:
  - quality
  layer:
  - testing
  enforcement: mandatory
  depends_on:
  - security
  - integration-testing
  consumed_by:
  - framework-qa-validation
  - ci-cd
  agent_roles:
  - control-agent
  - delivery-agent
  validation_profile: security-review
  mcp_usage: none
---

# security-testing

## Propósito

Esta skill define cómo validar la seguridad de la aplicación mediante pruebas ofensivas automatizadas: análisis estático (SAST), análisis dinámico (DAST), escaneo de dependencias (bun audit, pip-audit), detección de secretos, testing de autenticación OAuth2/Keycloak y gates de seguridad en CI.  
Su función es asegurar que los controles defensivos definidos en `security` y `framework-security` realmente funcionen bajo ataque, detectando vulnerabilidades antes de que lleguen a producción.

Esta skill complementa `security` (controles defensivos) y `framework-security` (RBAC, guardrails). Mientras esas definen QUÉ proteger, esta skill valida QUE la protección funciona.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Qué herramientas de SAST y DAST usar?
2. ¿Cómo se escanean dependencias vulnerables?
3. ¿Cómo se detectan secretos expuestos en el código?
4. ¿Qué security gates se configuran en CI/CD?
5. ¿Cómo se reportan y priorizan las vulnerabilidades encontradas?

## Relación con otras skills

- `security` define los controles defensivos (OWASP Top 10) que esta skill valida.
- `authentication` y `authorization` definen los mecanismos que esta skill ataca.
- `integration-testing` establece la base funcional que esta skill extiende con seguridad.
- `framework-security` define los guardrails del framework que esta skill valida.
- `ci-cd` ejecuta los security gates en el pipeline.

## Qué debe hacer el agente cuando esta skill está activa

1. Configurar SAST en el proyecto (SonarQube, Semgrep, o equivalente).
2. Configurar DAST en el pipeline (OWASP ZAP o equivalente).
3. Configurar escaneo de dependencias (Snyk, Dependabot, pip-audit).
4. Configurar detección de secretos (git-secrets, truffleHog, o Gitleaks).
5. Definir security gates en CI que bloqueen el merge si hay vulnerabilidades críticas o altas.
6. Ejecutar escaneo SAST en cada PR.
7. Ejecutar escaneo DAST en cada deploy a staging.
8. Documentar y priorizar las vulnerabilidades encontradas.

## Entradas esperadas

Esta skill asume que ya existe:
- controles de seguridad implementados (`security`, `authentication`, `authorization`);
- tests de integración pasando (`integration-testing`);
- pipeline de CI configurado (`ci-cd`).

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase sí incluye:
- SAST (Static Application Security Testing);
- DAST (Dynamic Application Security Testing);
- Dependency scanning;
- Secret scanning;
- Security gates en CI;
- Reporte y priorización de vulnerabilidades.

La fase no incluye todavía:
- Penetration testing manual (se recomienda, pero está fuera de scope);
- Bug bounty programs;
- Compliance audits (SOC2, ISO 27001);
- Security training para desarrolladores.

## Principios que siempre debe respetar

- Las vulnerabilidades CRÍTICAS y ALTAS DEBEN bloquear el merge en CI.
- Las vulnerabilidades MEDIAS DEBEN ser documentadas con plan de remediación.
- Las vulnerabilidades BAJAS PUEDEN ser aceptadas con justificación explícita.
- Los secretos NUNCA deben estar en el código fuente (ni en `.env` commiteado).
- Las dependencias con CVEs críticos DEBEN actualizarse antes del merge.
- Los resultados de SAST y DAST DEBEN ser accesibles en el PR (no en un dashboard separado).
- Los false positives DEBEN documentarse y marcarse como tales (no simplemente ignorarse).

## Qué decide esta skill y qué delega

Esta skill sí decide:
- las herramientas de SAST/DAST/dependency scanning;
- los security gates en CI;
- la priorización de vulnerabilidades;
- los umbrales de bloqueo.

Esta skill delega:
- los controles defensivos a `security`;
- la autenticación a `authentication`;
- la autorización a `authorization`;
- la ejecución del pipeline a `ci-cd`.

## Qué debe definir el diseño

### 1. Herramientas de SAST

| Herramienta | Stack | Pros | Contras | Uso recomendado |
|------------|-------|------|---------|-----------------|
| **Semgrep** | Multi-lenguaje | Reglas custom, rápido, CI-friendly, gratis | Reglas limitadas para lenguajes niche | **Por defecto** |
| **SonarQube** | Multi-lenguaje | Dashboard rico, quality gates, deuda técnica | Requiere servidor, pesado | Proyectos con servidor CI dedicado |
| **CodeQL** | Multi-lenguaje | Propiedad de GitHub, integrado en GitHub | Requiere GitHub Advanced Security | Proyectos en GitHub con GHE |
| **ESLint security** | JS/TS | Ya en el proyecto, lightweight | Solo JS/TS | Complementario |

**Decisión por defecto**: Semgrep + ESLint security plugins.

### 2. Herramientas de DAST

| Herramienta | Pros | Contras | Uso recomendado |
|------------|------|---------|-----------------|
| **OWASP ZAP** | Gratis, estándar de la industria, Docker | Lento, false positives | **Por defecto** |
| **Nuclei** | Rápido, templates actualizados, CI-friendly | Menos completo que ZAP | Para escaneos rápidos en CI |

**Decisión por defecto**: OWASP ZAP en Docker para DAST completo, Nuclei para escaneos rápidos.

### 3. Escaneo de dependencias

| Herramienta | Pros | Contras | Uso recomendado |
|------------|------|---------|-----------------|
| **Snyk** | Amplia base de CVEs, auto-fix | Comercial | Proyectos con presupuesto |
| **Dependabot** | Gratuito, integrado en GitHub | Solo GitHub | **Por defecto** |
| **bun audit** | Nativo de Bun, rápido, sin setup extra | Solo ecosistema npm/bun | **Por defecto (Bun)** |
| **pip-audit** | Nativo de Python, PyPI DB | Solo Python | **Por defecto (Python)** |
| **Trivy** | Gratis, escanea containers | Requiere Docker | Para imágenes Docker |

**Decisión por defecto**: `bun audit` para dependencias TS/JS + `pip-audit` para dependencias Python + Dependabot (GitHub) + Trivy para imágenes Docker.

### 4. Detección de secretos

| Herramienta | Pros | Contras | Uso recomendado |
|------------|------|---------|-----------------|
| **Gitleaks** | Rápido, pre-commit hook | Solo git history | **Por defecto** |
| **truffleHog** | Escanea todo el history | Lento en repos grandes | Auditoría completa |
| **git-secrets** | Pre-commit hook simple | Menos tipos de secretos | Alternativa ligera |

**Decisión por defecto**: Gitleaks como pre-commit hook + CI step.

### 5. Configuración de Semgrep

```yaml
# .semgrep.yml
rules:
  - id: sql-injection
    patterns:
      - pattern: |
          string query = "SELECT * FROM " + $TABLE + " WHERE " + $COND;
      - pattern: |
          $CONN.Query($QUERY, ...);
    message: Potential SQL injection. Use parameterized queries.
    severity: ERROR
    languages: [python]

  - id: hardcoded-secret
    patterns:
      - pattern: |
          password = "..."
      - pattern: |
          api_key = "..."
      - pattern: |
          secret = "..."
    message: Hardcoded secret detected. Use environment variables or secret management.
    severity: ERROR
    languages: [generic]
```

### 6. OWASP ZAP en Docker

```yaml
# docker-compose.security.yml
version: '3.8'
services:
  zap:
    image: zaproxy/zap-stable
    command:zap-baseline.py -t ${TARGET_URL} -J zap-report.json || true
    volumes:
      - ./reports:/zap/reports
    networks:
      - security-test

  app:
    build: .
    environment:
      # Bun (backend general / TypeScript)
      - BUN_ENV=staging
      - NODE_ENV=staging
      # FastAPI (AI/ML core / Python)
      - APP_ENV=staging
      - FASTAPI_ENV=staging
      - UVICORN_WORKERS=2
      # Infraestructura
      - DATABASE_URL=postgresql://user:pass@db:5432/app_staging
      - REDIS_URL=redis://redis:6379
      - KEYCLOAK_URL=http://keycloak:8080
      - KEYCLOAK_REALM=staging
      - KEYCLOAK_CLIENT_ID=app-staging
    networks:
      - security-test

networks:
  security-test:
```

### 7. Security gates en CI

```yaml
# .github/workflows/security.yml
name: Security
on:
  pull_request:
    branches: [main, develop]
  schedule:
    - cron: '0 3 * * 1'  # Weekly Monday at 3 AM

jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/secrets
            p/owasp-top-ten
          publishToken: ${{ secrets.SEMGREP_APP_TOKEN }}

  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Snyk
        uses: snyk/actions/node@master
        with:
          args: --severity-threshold=high
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}

  dast:
    runs-on: ubuntu-latest
    needs: [sast, dependency-scan]
    if: github.event_name == 'schedule'
    steps:
      - uses: actions/checkout@v4
      - name: OWASP ZAP Baseline Scan
        uses: zaproxy/action-baseline@v0.12.0
        with:
          target: ${{ secrets.STAGING_URL }}
          rules_file_name: 'zap-rules.tsv'
          cmd_options: '-a -j'
```

### 8. Clasificación y priorización de vulnerabilidades

| Severidad | CVSS | Acción | Gate en CI |
|-----------|------|--------|------------|
| **Crítica** | 9.0-10.0 | Bloquear merge inmediatamente. Remediación en < 24h. | BLOCK |
| **Alta** | 7.0-8.9 | Bloquear merge. Remediación en < 7 días. | BLOCK |
| **Media** | 4.0-6.9 | Permitir merge con justificación. Remediación en < 30 días. | WARN |
| **Baja** | 0.1-3.9 | Aceptar con justificación. Remediación planificada. | INFO |

### 9. Checklist de seguridad por OWASP Top 10

| # | Riesgo OWASP | Verificación recomendada |
|---|-------------|------------------------|
| A01 | Broken Access Control | ZAP active scan, test de autorización por rol |
| A02 | Cryptographic Failures | Semgrep: uso de HTTP, algoritmos débiles, TLS version |
| A03 | Injection | Semgrep: SQL concatenado, command injection, XSS |
| A04 | Insecure Design | Revisión manual de diseño de autorización |
| A05 | Security Misconfiguration | ZAP: headers faltantes (CSP, HSTS, X-Frame-Options) |
| A06 | Vulnerable Components | Snyk/Dependabot: CVEs en dependencias |
| A07 | Auth Failures | ZAP: fuerza bruta, sesión débil, logout sin invalidar |
| A08 | Software/Data Integrity | Semgrep: uso de CDN sin SRI, deserialización insegura |
| A09 | Logging/Monitoring Failures | Revisión manual: logs de seguridad, alertas |
| A10 | SSRF | Semgrep: URLs de usuario sin validación, fetch sin whitelist |

### 10. Testing de autenticación OAuth2/Keycloak

El stack del framework usa **Keycloak** como IdP centralizado. Los tests de seguridad deben validar el flujo OAuth2/OIDC completo:

#### Endpoints críticos a auditar

| Endpoint | Qué validar |
|----------|-------------|
| `/realms/{realm}/protocol/openid-connect/auth` | No expone tokens en URL, state parameter requerido |
| `/realms/{realm}/protocol/openid-connect/token` | Rate limiting, no acepta grant_type inválido |
| `/realms/{realm}/protocol/openid-connect/userinfo` | Solo acepta token válido, no expone PII innecesaria |
| `/realms/{realm}/protocol/openid-connect/certs` | JWKS expone solo claves públicas |
| `/admin/realms/{realm}` | Acceso restringido a admins, no expuesto externamente |

#### Tests automatizados recomendados

| Categoría | Qué probar | Herramienta |
|-----------|-----------|-------------|
| **Token validation** | Tokens expirados rechazados, tokens con issuer inválido rechazados | pytest + httpx |
| **Token introspection** | `/introspect` devuelve estado activo/inactivo, no expone claims sensibles a clientes no autorizados | pytest + httpx |
| **Scope enforcement** | Endpoints rechazan requests sin scope requerido | pytest + httpx |
| **RBAC bypass** | Intento de acceso con rol insuficiente devuelve 403 | pytest + httpx |
| **Session fixation** | Logout invalida el token en Keycloak (no solo en la app) | pytest + httpx |
| **Token replay** | Token usado después de logout es rechazado | pytest + httpx |
| **CORS** | Keycloak no acepta requests de origins no configurados | OWASP ZAP |
| **Rate limiting** | Login con credenciales inválidas tiene rate limit | k6 / Locust |
| **PKCE** | Flow authorization_code con PKCE funciona correctamente | pytest + httpx |

#### Configuración de ZAP para OAuth2

```yaml
# zap-oauth2-config.yml
authentication:
  method: "authenticationProvider"
  parameters:
    authenticationProvider: "OAuth2AuthenticationMethod"
    tokenEndpoint: "http://keycloak:8080/realms/staging/protocol/openid-connect/token"
    clientId: "app-staging"
    clientSecret: "${KEYCLOAK_CLIENT_SECRET}"
    refreshToken: "${OAUTH2_REFRESH_TOKEN}"
    tokensSentAs: "HEADER"
```

#### Variables de entorno para testing de auth

```bash
# .env.security-test
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=staging
KEYCLOAK_CLIENT_ID=app-staging
KEYCLOAK_CLIENT_SECRET=<from-vault>
OAUTH2_REFRESH_TOKEN=<obtained-from-setup>
```

### 11. Seguridad en operaciones pgvector

El stack del framework usa **PostgreSQL + pgvector** para embeddings y búsqueda semántica. Las operaciones vectoriales introducen riesgos específicos que deben validarse:

#### Riesgos específicos de pgvector

| Riesgo | Descripción | Mitigación / Test |
|--------|-------------|------------------|
| **Inyección en queries vectoriales** | Concatenar embeddings o metadatos en SQL raw permite inyección | Usar parámetros bindados; Semgrep rule para `execute` con f-strings en queries vectoriales |
| **Fuga de embeddings cross-tenant** | `ORDER BY embedding <=> $1` sin filtro de `tenant_id` devuelve vectores de otros tenants | Forzar `WHERE tenant_id = $tenant` en toda query vectorial; test de aislamiento multi-tenant |
| **Dimensionalidad inconsistente** | Embeddings de dimensión distinta causan errores o comportamientos inesperados | Validar `vector_dims` en DTO antes de insertar; test con vectores de dimensión incorrecta |
| **Reconstrucción de datos privados** | Embeddings pueden invertirse para inferir contenido original (model inversion) | Cifrar PII antes de embedding; no almacenar texto plano junto al vector sin control de acceso |
| **Costo/DoS por KNN** | `K` muy alto en búsqueda vectorial degrada performance y permite DoS | Limitar `K` (top_k) a un máximo razonable (ej. 100); rate limiting en endpoints de búsqueda semántica |
| **Índices HNSW/IVFFlat expuestos** | Configuración de índices puede filtrar estructura de datos | No exponer metadatos de índices vía API; restringir endpoints de admin de BD |

#### Regla Semgrep para queries vectoriales

```yaml
# .semgrep.yml (adicional)
rules:
  - id: pgvector-raw-query-injection
    pattern: |
      $SESSION.execute(f"SELECT ... embedding <=> $VEC ...")
    message: Posible inyección SQL en query vectorial. Usar parámetros bindados.
    severity: ERROR
    languages: [python]

  - id: pgvector-missing-tenant-filter
    pattern: |
      $SESSION.execute("SELECT ... ORDER BY embedding <=> $VEC", ...)
    message: Query vectorial sin filtro de tenant_id. Verificar aislamiento multi-tenant.
    severity: WARNING
    languages: [python]
```

#### Tests recomendados para pgvector

| Categoría | Qué probar | Herramienta |
|-----------|-----------|-------------|
| **Aislamiento multi-tenant** | Búsqueda semántica de tenant A no devuelve vectores de tenant B | pytest + TestContainers |
| **Validación de dimensión** | Insertar vector de dimensión incorrecta devuelve 422 | pytest + httpx |
| **Límite de top_k** | `top_k > MAX_K` devuelve 422 o se trunca | pytest + httpx |
| **Inyección en metadatos** | Filtros de metadatos con SQL injection son sanitizados | pytest + httpx |
| **Acceso a embeddings raw** | Endpoint que devuelve embeddings raw está protegido por scope admin | pytest + httpx |

## Preguntas guía

### 1. Sobre herramientas
- ¿Se usa Semgrep, SonarQube o CodeQL para SAST?
- ¿Se usa OWASP ZAP o Nuclei para DAST?
- ¿Se usa bun audit, pip-audit, Dependabot o Snyk para dependencias?
- ¿Se usa Gitleaks o truffleHog para detección?

### 2. Sobre gates
- ¿Qué severidad bloquea el merge?
- ¿Los false positives se documentan como excepciones?
- ¿Quién aprueba las excepciones?

### 3. Sobre secretos
- ¿Los secretos están en variables de entorno o vault (no en código)?
- ¿Hay pre-commit hook para prevenir commits con secretos?

### 4. Sobre DAST
- ¿Se ejecuta ZAP contra staging?
- ¿Se prueban endpoints autenticados (OAuth2/Keycloak)?
- ¿Los resultados de DAST se incluyen en el PR?

### 5. Sobre dependencias
- ¿Se escanean dependencias transitivas (bun audit + pip-audit)?
- ¿Las CVEs críticas se actualizan automáticamente?
- ¿Se escanean imágenes Docker con Trivy?

### 6. Sobre autenticación
- ¿Se validan tokens expirados, scopes y RBAC en Keycloak?
- ¿Se prueba PKCE y token replay?
- ¿Keycloak admin endpoint está protegido externamente?

## Salidas esperadas de esta skill

### A. Configuración de SAST
- `.semgrep.yml` con reglas de seguridad.
- Workflow de CI con step de Semgrep.

### B. Configuración de DAST
- `docker-compose.security.yml` con OWASP ZAP.
- Script de ejecución de ZAP baseline scan.

### C. Escaneo de dependencias
- Dependabot configurado en repository.
- `bun audit` como step de CI para dependencias TS/JS.
- `pip-audit` como step de CI para dependencias Python.

### D. Detección de secretos
- Gitleaks pre-commit hook configurado.
- Step de CI para escaneo de secretos.

### E. Security gates en CI
- Workflow `.github/workflows/security.yml` con SAST, dependency-scan, secret-scan, DAST.
- Gates configurados: CRÍTICA y ALTA bloquean merge.

### F. Consumidores de esta skill
- `framework-qa-validation` usa los security gates como criterio go/no-go;
- `ci-cd` ejecuta los security gates en el pipeline;
- `security` define los controles defensivos que esta skill valida;
- `framework-security` define los guardrails que esta skill verifica.

## Criterios de calidad

- SAST está configurado y se ejecuta en cada PR.
- DAST está configurado y se ejecuta en cada deploy a staging.
- Dependabot o Snyk está configurado para dependencias.
- Gitleaks está configurado como pre-commit hook y CI step.
- Las vulnerabilidades CRÍTICAS y ALTAS bloquean el merge.
- Los false positives están documentados como excepciones.
- Los resultados de seguridad son visibles en el PR.
- El checklist OWASP Top 10 está verificado.

## Comportamiento esperado del agente

Cuando el usuario quiera deshabilitar un security gate, el agente debe exigir una justificación explícita y registrar la excepción.  
Cuando se encuentre un false positive, el agente debe documentarlo como excepción con explicación, no simplemente ignorarlo.  
Cuando se encuentre una vulnerabilidad CRÍTICA, el agente debe bloquear el merge y proponer remediación inmediata.  
Cuando el usuario no tenga entorno de staging para DAST, el agente debe proponer OWASP ZAP con Docker.

## Checklist final de la skill

- ¿Se configuró SAST (Semgrep/SonarQube)?
- ¿Se configuró DAST (OWASP ZAP)?
- ¿Se configuró escaneo de dependencias TS/JS (`bun audit`)?
- ¿Se configuró escaneo de dependencias Python (`pip-audit`)?
- ¿Se configuró escaneo de dependencias (Dependabot/Snyk)?
- ¿Se configuró detección de secretos (Gitleaks)?
- ¿Los security gates bloquean CRÍTICA y ALTA?
- ¿Los resultados son visibles en el PR?
- ¿Se ejecutó el checklist OWASP Top 10?
- ¿Se validó autenticación OAuth2/Keycloak (tokens, scopes, RBAC, PKCE, introspection)?
- ¿Keycloak admin endpoint está protegido externamente?
- ¿Se validó seguridad en operaciones pgvector (aislamiento tenant, inyección, dimensión, top_k)?
- ¿Los false positives están documentados?
- ¿Se configuró DAST contra staging?
- ¿Se definió el proceso de remediación por severidad?