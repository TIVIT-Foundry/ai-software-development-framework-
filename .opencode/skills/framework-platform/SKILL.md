---
name: framework-platform
description: 'Usa esta skill para diseñar la plataforma e infraestructura del framework.
  Sirve para definir cómputo, Kubernetes, despliegue, namespaces por tenant, workflows
  largos, mensajería, observabilidad, CI/CD, resiliencia, rollback, tagging de costos
  y operación multi-tenant. Trigger: Cuando se necesita diseñar la plataforma: K8s,
  despliegue, namespaces, mensajería, observabilidad y operación multi-tenant.'
version: 1.0
metadata:
  when_to_use:
  - Cuando se necesita diseñar la capa 7 del framework.
  - Cuando se quiere definir cómo correrá el framework en cloud, híbrido u on-premise.
  - Cuando se requiere aterrizar despliegue, runtime, observabilidad y operación.
  - Cuando se necesita resolver escalado, aislamiento por tenant y costos por workload.
  - Cuando se prepara la solución para producción o para un MVP operable.
  phase:
  - operations
  layer:
  - infrastructure
  enforcement: mandatory
  depends_on:
  - framework-architecture
  - framework-security
  - framework-data-memory-compliance
  consumed_by:
  - framework-scaffold-implementation
  - framework-operations-evolution
  agent_roles:
  - delivery-agent
  - control-agent
  validation_profile: architecture-consistency
  mcp_usage: governed
---

# framework-platform

## Propósito

Esta skill sirve para diseñar la plataforma técnica que soporta la ejecución del framework en operación real.  
Su función es definir cómo se despliegan y operan los componentes, cómo se escala el sistema, cómo se soporta multi-tenancy en runtime, cómo se monitorea la salud y cómo se mantiene portabilidad entre entornos.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Dónde y cómo corre cada componente del framework?
2. ¿Qué partes deben correr sobre Kubernetes y cuáles pueden ser servicios gestionados?
3. ¿Cómo se implementan workflows largos y mensajería asíncrona?
4. ¿Cómo se despliega sin romper disponibilidad ni compatibilidad?
5. ¿Cómo se monitorean salud, performance, costo y errores?
6. ¿Cómo se escala por tenant, carga y criticidad?
7. ¿Cómo se asegura portabilidad entre cloud y on-premise?
8. ¿Cómo se controlan costos operativos a nivel de workload y tenant?

## Relación con otras skills

- `framework-architecture` define la topología lógica y las dependencias que esta skill convierte en runtime operable.
- `framework-security` define controles, secretos, políticas y trazabilidad que esta skill debe materializar operativamente.
- `framework-data-memory-compliance` define stores, aislamiento, residencia y retención que esta skill debe soportar en ejecución.
- `framework-operations-evolution` consume esta skill para convertir observabilidad, release y resiliencia en operación continua.
- `framework-scaffold-implementation` usa esta skill como baseline para el primer entorno ejecutable y pipelines iniciales.

## Qué debe hacer el agente cuando esta skill está activa

El agente debe:

1. Diseñar la topología de runtime del framework.
2. Identificar componentes desplegables y sus dependencias.
3. Definir qué corre en Kubernetes y qué se consume como managed service.
4. Diseñar mensajería, colas y workflows largos.
5. Definir observabilidad técnica y operativa.
6. Diseñar CI/CD, estrategias de release y rollback.
7. Proponer aislamiento y escalado por tenant cuando aplique.
8. Incluir tagging, cuotas y visibilidad de costos.
9. Mantener portabilidad como criterio arquitectónico.
10. Proponer una versión mínima operable para MVP y una evolución posterior.

## Entradas esperadas

Esta skill asume que ya existe:
- gobierno del framework;
- arquitectura general;
- diseño del core;
- diseño de seguridad;
- idea clara de los componentes principales y su criticidad.

Si no existe esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase de plataforma e infraestructura sí incluye:
- cómputo base;
- contenedores y Kubernetes;
- namespaces y aislamiento en runtime;
- networking interno;
- mensajería;
- workflows largos;
- observabilidad;
- CI/CD;
- release management;
- rollback;
- escalado;
- resiliencia;
- costos por workload.

La fase de plataforma e infraestructura no incluye todavía:
- hardening profundo de cada cluster específico;
- ejecución real de despliegues;
- administración diaria de SRE completa;
- negociación comercial con proveedores cloud.

## Principios que siempre debe respetar

- La lógica propia del framework debe correr sobre Kubernetes estándar.
- La plataforma debe permitir mover la solución entre cloud y on-premise con el menor cambio posible.
- Los componentes deben ser observables desde el primer día.
- Los workflows largos y eventos asíncronos deben tratarse como capacidades de plataforma, no hacks ad hoc.
- El costo debe ser visible por tenant y por workload.
- El escalado debe responder a carga, criticidad y aislamiento requerido.
- El pipeline de entrega debe permitir cambios frecuentes con riesgo controlado.
- La plataforma debe ser suficiente para MVP sin impedir evolución enterprise.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- la topología de runtime y despliegue;
- qué corre en Kubernetes y qué se externaliza;
- mensajería, workflows largos y resiliencia;
- observabilidad base, CI/CD y rollback;
- costos, cuotas y aislamiento operativo por tenant.

Esta skill delega:
- políticas de seguridad y autorización a `framework-security`;
- taxonomía de datos, retención y clasificación a `framework-data-memory-compliance`;
- contratos del core y del pack a `framework-core-design` y `framework-pack-design`;
- ownership operativo, SLOs y proceso de incidentes a `framework-operations-evolution`.

## Qué debe definir el diseño

### 1. Topología general
Definir:
- componentes desplegables;
- servicios internos;
- servicios externos gestionados;
- dependencias runtime;
- fronteras entre plano de ejecución, datos y observabilidad.

### 2. Estrategia de cómputo
Definir:
- qué corre en Kubernetes;
- qué puede correr en serverless efímero;
- qué workloads son batch;
- qué workloads son always-on;
- qué componentes requieren HA;
- afinidad o separación de cargas críticas.

### 3. Kubernetes
Definir:
- cluster topology;
- namespaces;
- políticas de red;
- quotas;
- autoscaling;
- nodos dedicados cuando aplique;
- entornos dev, qa, prod;
- estrategia de portabilidad entre GKE, EKS, AKS u on-premise.

### 4. Aislamiento por tenant en runtime
Definir:
- si el aislamiento es lógico o con namespaces dedicados;
- criterios para tenants premium o regulados;
- límites de recursos;
- network isolation;
- observabilidad y tagging por tenant.

### 5. Workflows largos
Definir:
- procesos que duran minutos, horas o días;
- orquestador como Temporal o equivalente;
- retries;
- compensaciones;
- visibilidad operativa;
- handoffs y reanudación.

### 6. Mensajería y eventos
Definir:
- broker o buses de eventos;
- casos de uso low-latency vs reliable delivery;
- colas;
- topics;
- contratos de eventos;
- reintentos;
- dead-letter queues;
- idempotencia.

### 7. Observabilidad
Definir:
- métricas;
- logs;
- traces;
- dashboards;
- alertas;
- SLOs;
- tagging por tenant, pack, agente y workload;
- correlación entre runtime, tools y costos.

### 8. CI/CD y release
Definir:
- pipeline de build, test y deploy;
- GitOps o estrategia equivalente;
- canary releases;
- feature flags;
- rollback automático;
- validaciones pre y post deploy;
- segregación por ambiente.

### 9. Resiliencia y continuidad operativa
Definir:
- retries;
- timeouts;
- circuit breakers;
- health checks;
- readiness/liveness;
- backups;
- restore;
- manejo de degradación;
- RTO/RPO si aplica.

### 10. Costos y capacidad
Definir:
- tagging de recursos;
- costo por workload;
- costo por tenant;
- presupuesto por entorno;
- límites de consumo;
- visibilidad de storage, cómputo, tráfico y modelos;
- criterios de rightsizing.

## Preguntas guía

### 1. Sobre runtime
- ¿Qué componentes necesitan correr siempre?
- ¿Qué componentes pueden ser efímeros?
- ¿Qué partes necesitan latencia baja y cuáles toleran asincronía?

### 2. Sobre Kubernetes
- ¿Qué partes justifican namespaces dedicados?
- ¿Qué política de separación se necesita por tenant o por ambiente?
- ¿Qué dependencias impedirían portar la solución a otro entorno?

### 3. Sobre workflows
- ¿Qué procesos no caben en una request síncrona?
- ¿Qué pasa si una ejecución se interrumpe a mitad?
- ¿Qué eventos deben sobrevivir reinicios o fallos parciales?

### 4. Sobre mensajería
- ¿Cuándo usar low-latency messaging y cuándo reliable delivery?
- ¿Qué eventos necesitan orden, replay o DLQ?
- ¿Qué consumidores deben ser idempotentes?

### 5. Sobre observabilidad
- ¿Qué necesita ver un operador?
- ¿Qué necesita ver un cliente enterprise?
- ¿Qué señales permiten detectar regresiones, costos anómalos o saturación?

### 6. Sobre entrega
- ¿Con qué frecuencia se desplegará?
- ¿Qué riesgo tolera cada ambiente?
- ¿Qué evidencia se necesita antes de promover cambios?

### 7. Sobre costos
- ¿Qué workload consume más?
- ¿Qué tenant requiere aislamiento premium?
- ¿Cómo se reflejan los costos de pods, storage, mensajería y modelos?

## Salidas esperadas de esta skill

Cuando esta skill responda, debe producir uno o varios de estos artefactos:

### A. Topología de plataforma
- componente;
- tipo;
- runtime;
- dependencia;
- criticidad.

### B. Diseño Kubernetes
- cluster;
- namespace;
- workload;
- aislamiento;
- escalado;
- observaciones.

### C. Diseño de workflows largos
- proceso;
- disparador;
- duración esperada;
- orquestador;
- retry;
- compensación.

### D. Diseño de mensajería
- evento;
- broker;
- productor;
- consumidor;
- garantía requerida;
- DLQ o retry.

### E. Estrategia de observabilidad
- señal;
- herramienta;
- etiqueta;
- umbral;
- destinatario.

### F. Pipeline CI/CD
- etapa;
- validación;
- criterio de promoción;
- rollback;
- evidencia.

### G. Política de resiliencia
- componente;
- fallo esperado;
- mitigación;
- fallback;
- recuperación.

### H. Modelo de costos
- recurso;
- unidad;
- tag;
- visibilidad;
- acción de control.

### I. Roadmap de madurez de plataforma
- MVP operable;
- siguiente nivel;
- nivel enterprise.

### J. Consumidores del diseño de plataforma
- consumidor;
- capacidad consumida;
- uso esperado;
- dependencia crítica.

## Criterios de calidad

La skill debe evaluar el diseño usando estos criterios:

- portabilidad real;
- simplicidad suficiente para MVP;
- capacidad de crecimiento;
- observabilidad útil;
- aislamiento por tenant cuando haga falta;
- resiliencia razonable;
- pipeline seguro y frecuente;
- visibilidad de costos;
- bajo acoplamiento a un proveedor específico.

## Comportamiento esperado del agente

Cuando una propuesta meta demasiados servicios gestionados que bloqueen portabilidad, el agente debe marcar el riesgo.  
Cuando una solución de MVP sea demasiado pesada, debe simplificar sin romper los principios base.  
Cuando un tenant regulado requiera más aislamiento, debe proponer namespaces o recursos dedicados.  
Cuando no exista observabilidad suficiente, debe tratarlo como defecto crítico de plataforma.
Cuando una decisión pertenezca al proceso operativo, severidad de incidentes o gobernanza del cambio, debe fijar la capacidad técnica y remitir el ownership a `framework-operations-evolution`.

## Plantilla de respuesta recomendada

Usa esta estructura:

1. Objetivo de plataforma.
2. Topología general.
3. Kubernetes y runtime.
4. Workflows largos y mensajería.
5. Observabilidad.
6. CI/CD y release.
7. Resiliencia y continuidad.
8. Costos y escalado por tenant.
9. Trade-offs.
10. Decisiones pendientes.

## Ejemplos de uso

### Ejemplo 1
Consulta: “Diseña la plataforma para el framework en una versión híbrida.”

Respuesta esperada:
- mantener la lógica propia sobre Kubernetes;
- separar servicios gestionados reemplazables;
- definir observabilidad, mensajería y CI/CD compatibles con portabilidad.

### Ejemplo 2
Consulta: “Queremos un MVP rápido pero sin hipotecar el futuro.”

Respuesta esperada:
- proponer topología reducida;
- usar mínimos componentes operables;
- conservar contratos y patrones que permitan evolucionar.

### Ejemplo 3
Consulta: “Un cliente enterprise quiere aislamiento fuerte.”

Respuesta esperada:
- evaluar namespaces dedicados, quotas y políticas de red;
- reforzar tagging, observabilidad y costos por tenant;
- ajustar pipeline y operación para ese nivel.

## Checklist final de la skill

Antes de cerrar una respuesta, verificar:

- ¿Se definió la topología de ejecución?
- ¿Se resolvió qué corre en Kubernetes y qué no?
- ¿Se diseñaron workflows largos y mensajería?
- ¿Se definió observabilidad útil?
- ¿Se diseñó CI/CD con rollback?
- ¿Se contempló resiliencia y continuidad?
- ¿Se resolvió escalado y aislamiento por tenant?
- ¿Se definió visibilidad de costos por workload?
- ¿Se mantuvo portabilidad como principio?
