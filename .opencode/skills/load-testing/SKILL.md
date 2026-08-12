---
name: load-testing
description: "Load and performance testing patterns. Covers k6/Gatling/Locust, test scenarios, load profiles, SLO validation, regression benchmarks, soak testing, and CI integration. Trigger: When validating system performance under load, setting SLOs for latency and throughput, or running stress tests."
version: 1.1
metadata:
  phase:
  - quality
  layer:
  - testing
  enforcement: recommended
  depends_on:
  - integration-testing
  consumed_by:
  - framework-qa-validation
  - framework-operations-evolution
  agent_roles:
  - delivery-agent
  - control-agent
  validation_profile: release-gate
  mcp_usage: none
---

# load-testing

## Propósito

Esta skill define cómo validar que el sistema soporta la carga esperada bajo condiciones realistas de uso.  
Su función es asegurar que los SLOs de latencia, throughput y disponibilidad se cumplen antes de producción, detectando cuellos de botella, memory leaks y degradación progresiva.

Esta skill complementa `unit-testing` (validación unitaria), `integration-testing` (validación entre servicios) y `playwright` (validación E2E). Mientras esas validan funcionalidad, esta skill valida rendimiento y estabilidad bajo carga.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Qué herramienta de load testing usar (k6, Gatling, Locust)?
2. ¿Cómo se definen perfiles de carga realistas?
3. ¿Cuáles son los SLOs de rendimiento (latencia P50/P95/P99, throughput, disponibilidad)?
4. ¿Cómo se detectan cuellos de botella y memory leaks?
5. ¿Cómo se integran los tests de carga en CI/CD?

## Relación con otras skills

- `integration-testing` establece la base de tests funcionales que esta skill extiende con carga.
- `performance` define los patrones de optimización que esta skill valida.
- `framework-qa-validation` define los gates de release que incluyen SLOs de rendimiento.
- `framework-operations-evolution` define los SLOs operativos que esta skill verifica.
- `api-versioning` puede requerir tests de carga por versión de API.

## Qué debe hacer el agente cuando esta skill está activa

1. Seleccionar la herramienta de load testing según el stack (k6 para JS/TS, Gatling para JVM, Locust para Python).
2. Definir perfiles de carga basados en datos de uso real o estimaciones.
3. Escribir escenarios de load testing que cubran los endpoints críticos.
4. Definir SLOs de rendimiento (latencia P50/P95/P99, throughput, error rate).
5. Ejecutar tests de carga en entornos que repliquen producción.
6. Analizar resultados: cuellos de botella, memory leaks, degradación.
7. Documentar hallazgos y recomendaciones de optimización.
8. Configurar ejecución de load tests en CI contra un entorno de staging.

## Entradas esperadas

Esta skill asume que ya existe:
- código de producción funcional (`backend-api`, `data-access`);
- tests de integración pasando (`integration-testing`);
- SLOs definidos o por definir (`framework-operations-evolution`);
- entorno de staging similar a producción.

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase sí incluye:
- selección de herramienta de load testing;
- definición de perfiles de carga (smoke, average, peak, stress, soak);
- escritura de escenarios de load testing;
- definición de SLOs de rendimiento;
- ejecución y análisis de resultados;
- detección de cuellos de botella y memory leaks;
- integración en CI;

La fase no incluye todavía:
- optimización de código (cubierta por `performance`);
- configuración de infraestructura (cubierta por `framework-platform`);
- tests E2E en navegador (cubiertos por `playwright`).

## Principios que siempre debe respetar

- Los tests de carga DEBEN ejecutarse en entornos que repliquen producción (similar CPU, memoria, red).
- Los SLOs DEBEN estar definidos ANTES de ejecutar tests de carga.
- Los tests de carga NUNCA deben ejecutarse contra producción sin autorización explícita.
- Los resultados DEBEN incluir latencia P50, P95, P99 (no solo promedio).
- Los tests de carga DEBEN incluir escenarios de carga normal, pico y estrés.
- Los hallazgos DEBEN documentarse con métricas específicas y recomendaciones accionables.
- Los SLOs NO deben ser aspiracionales; deben basarse en datos reales de uso o estimaciones conservadoras.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- la herramienta de load testing;
- los perfiles de carga y escenarios;
- los SLOs de rendimiento;
- los umbrales de aprobación/rechazo.

Esta skill delega:
- la optimización de código a `performance`;
- la configuración de infraestructura a `framework-platform`;
- los SLOs operativos a `framework-operations-evolution`;
- los gates de release a `framework-qa-validation`.

## Qué debe definir el diseño

### 1. Herramientas de load testing

| Herramienta | Stack | Pros | Contras | Uso recomendado |
|------------|-------|------|---------|-----------------|
| **k6** | JS/TS | Scripts en JS, métricas en tiempo real, extensible, CI-friendly | No soporta UI testing | **Por defecto para APIs** |
| **Gatling** | JVM/Scala | DSL expresivo, reportes HTML ricos, soporta WebSocket | Requiere JVM, DSL no trivial | Proyectos JVM, escalabilidad masiva |
| **Locust** | Python | Python, UI web en tiempo real, distribuido | Más lento por proceso | Proyectos Python, prototipado rápido |
| **Artillery** | JS/YAML | YAML config, soporta HTTP/WebSocket/socket.io | Menos extensible que k6 | Tests rápidos en YAML |

**Decisión por defecto**: k6 para APIs y servicios, Gatling si el proyecto es JVM.

### 2. Perfiles de carga

| Perfil | Descripción | Duración | Objetivo |
|--------|-------------|----------|----------|
| **Smoke** | Carga mínima, verificar que funciona | 1-5 min | Verificar que el sistema responde |
| **Average** | Carga promedio esperada | 15-30 min | Validar SLOs en condiciones normales |
| **Peak** | Pico de carga esperado (día laborable) | 10-15 min | Validar SLOs en pico |
| **Stress** | Carga por encima del pico esperado | 10-15 min | Encontrar límites del sistema |
| **Soak** | Carga promedio sostenida por tiempo prolongado | 1-4 horas | Detectar memory leaks y degradación |
| **Spike** | Incremento súbito de 0 a pico | 5-10 min | Validar auto-scaling y resiliencia |

### 3. SLOs de rendimiento

| Métrica | SLO típicos | Medición |
|---------|-------------|----------|
| Latencia P50 | < 100ms | Percentil 50 de tiempo de respuesta |
| Latencia P95 | < 500ms | Percentil 95 de tiempo de respuesta |
| Latencia P99 | < 1000ms | Percentil 99 de tiempo de respuesta |
| Throughput | > 1000 RPS | Requests por segundo |
| Error rate | < 1% | Porcentaje de respuestas 5xx |
| Availability | > 99.9% | Uptime durante el test |
| CPU | < 70% | Uso de CPU bajo carga |
| Memory | < 80% | Uso de memoria bajo carga |

Regla: Los SLOs se definen por endpoint, no globales. Endpoints críticos (login, checkout) tienen SLOs más estrictos que endpoints secundarios.

### 4. Estructura de tests k6

```
tests/
├── load/
│   ├── scenarios/
│   │   ├── smoke.js
│   │   ├── average.js
│   │   ├── peak.js
│   │   ├── stress.js
│   │   ├── soak.js
│   │   └── spike.js
│   ├── helpers/
│   │   ├── auth.js
│   │   ├── data-generator.js
│   │   └── thresholds.js
│   └── config/
│       ├── staging.json
│       └── production-like.json
├── k6.config.js
└── package.json
```

### 5. Ejemplo de script k6 (smoke test)

```javascript
// tests/load/scenarios/smoke.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const latency = new Trend('latency');

export const options = {
  stages: [
    { duration: '30s', target: 20 },  // Ramp up to 20 VUs
    { duration: '1m', target: 20 },   // Stay at 20 VUs
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    errors: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';

export default function () {
  // List entities
  const listRes = http.get(`${BASE_URL}/api/v1/entities`, {
    headers: { Authorization: `Bearer ${__ENV.AUTH_TOKEN}` },
  });

  check(listRes, {
    'list status is 200': (r) => r.status === 200,
    'list has data': (r) => JSON.parse(r.body).data.length > 0,
  });

  errorRate.add(listRes.status >= 400);
  latency.add(listRes.timings.duration);

  sleep(1);
}
```

### 6. Ejemplo de thresholds por SLO

```javascript
// tests/load/helpers/thresholds.js
export const standardThresholds = {
  http_req_duration: ['p(50)<100', 'p(95)<500', 'p(99)<1000'],
  http_req_failed: ['rate<0.01'],
  iterations: ['count > 1000'],
};

export const criticalThresholds = {
  http_req_duration: ['p(50)<50', 'p(95)<200', 'p(99)<500'],
  http_req_failed: ['rate<0.001'],
  iterations: ['count > 5000'],
};
```

### 7. Integración en CI/CD

```yaml
# .github/workflows/load-test.yml
name: Load Tests
on:
  pull_request:
    types: [labeled]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC

jobs:
  load-test:
    if: contains(github.event.pull_request.labels.*.name, 'run-load-test') || github.event_name == 'schedule'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: grafana/setup-k6-action@v1
      - uses: grafana/run-k6-action@v1
        with:
          path: |
            tests/load/scenarios/average.js
        env:
          BASE_URL: ${{ secrets.STAGING_URL }}
          AUTH_TOKEN: ${{ secrets.LOAD_TEST_TOKEN }}
      - name: Check thresholds
        run: |
          # k6 exits with non-zero if thresholds are breached
          echo "Load test completed. Check Grafana dashboard for details."
```

### 8. Checklist de resultados

Después de cada ejecución de load testing:

- [ ] P50 latency dentro del SLO para TODOS los endpoints
- [ ] P95 latency dentro del SLO para endpoints críticos
- [ ] P99 latency dentro del SLO para endpoints críticos
- [ ] Error rate < 1% (o < 0.1% para endpoints críticos)
- [ ] Throughput alcanza el mínimo esperado
- [ ] CPU < 70% bajo carga promedio
- [ ] Memory < 80% bajo carga promedio y no crece en soak test
- [ ] No hay memory leaks detectados en soak test
- [ ] Auto-scaling funciona correctamente en spike test
- [ ] Resultados documentados con métricas específicas

## Preguntas guía

### 1. Sobre perfiles
- ¿Cuál es la carga promedio esperada (RPS)?
- ¿Cuál es el pico esperado (RPS y usuarios concurrentes)?
- ¿Hay patrones estacionales (Black Friday, fin de mes)?

### 2. Sobre SLOs
- ¿Cuáles son los SLOs de latencia por endpoint?
- ¿Cuál es el error rate máximo aceptable?
- ¿Los SLOs están alineados con `framework-operations-evolution`?

### 3. Sobre herramientas
- ¿Se usa k6, Gatling o Locust?
- ¿Los resultados se envían a Grafana/Datadog?
- ¿Los tests de carga corren en CI o son manuales?

### 4. Sobre entorno
- ¿El entorno de staging replica producción?
- ¿Se necesita data seeding para los tests?
- ¿Cómo se obtienen tokens de autenticación para los tests?

### 5. Sobre CI
- ¿Los tests de carga corren en cada PR o solo en nightly?
- ¿Hay gates que bloqueen el merge si los SLOs no se cumplen?
- ¿Quién es responsable de analizar los resultados?

## Salidas esperadas de esta skill

### A. Proyecto de load testing configurado
- Directorio `tests/load/` con escenarios, helpers y config.
- Scripts k6 para cada perfil de carga (smoke, average, peak, stress, soak, spike).
- Thresholds por SLO configurados.

### B. SLOs de rendimiento documentados
- Tabla de SLOs por endpoint (P50, P95, P99, throughput, error rate).
- Thresholds correspondientes en los scripts.

### C. Integración CI/CD
- Workflow de GitHub Actions para load testing.
- Ejecución en PR con label `run-load-test`.
- Ejecución nightly automática.

### D. Reporte de resultados
- Latencia P50/P95/P99 por endpoint.
- Throughput alcanzado vs esperado.
- Error rate.
- Consumo de CPU y memoria.
- Hallazgos y recomendaciones.

### E. Consumidores de esta skill
- `framework-qa-validation` usa los SLOs como gates de release;
- `framework-operations-evolution` define los SLOs operativos que esta skill verifica;
- `performance` recibe las recomendaciones de optimización;
- `ci-cd` ejecuta los tests de carga en el pipeline.

## Criterios de calidad

- SLOs están definidos por endpoint antes de ejecutar tests.
- Se prueban al menos 3 perfiles (smoke, average, peak).
- Se incluye un soak test para detección de memory leaks.
- Los SLOs incluyen P50, P95 y P99 (no solo promedio).
- Los tests se ejecutan en entorno similar a producción.
- Los resultados se documentan con métricas específicas.
- Los hallazgos tienen recomendaciones accionables.
- La integración CI está configurada.

## Comportamiento esperado del agente

Cuando el usuario defina SLOs sin datos de uso real, el agente debe sugerir perfiles de carga conservadores y recommendar instrumentar la aplicación primero.  
Cuando el usuario quiera ejecutar load tests contra producción, el agente debe rechazar y proponer un entorno de staging.  
Cuando los resultados muestren latencia P99 > SLO, el agente debe derivar a `performance` para optimización.  
Cuando se detecte un memory leak en soak test, el agente debe sugerir profiling de memoria y heap dump.

## Checklist final de la skill

- ¿Se seleccionó la herramienta de load testing?
- ¿Se definieron SLOs por endpoint?
- ¿Se escribieron escenarios para al menos 3 perfiles?
- ¿Se incluye un soak test?
- ¿Los threshold incluyen P50, P95 y P99?
- ¿Se probó en entorno similar a producción?
- ¿Se documentaron los resultados con métricas?
- ¿Se configuró la integración CI?
- ¿Se derivó a `performance` si hay hallazgos de optimización?
- ¿Los SLOs están alineados con `framework-operations-evolution`?