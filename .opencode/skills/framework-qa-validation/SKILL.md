---
name: framework-qa-validation
description: 'Usa esta skill para diseñar la capa de QA y validación del framework.
  Sirve para definir estrategias de prueba por capa, contract tests, integración,
  end-to-end, validación de guardrails, multi-tenancy, trazabilidad, criterios de
  aceptación y go/no-go. Trigger: Cuando ya existe scaffold y se necesita validar:
  estrategia de pruebas, contract tests, trazabilidad y criterios go/no-go.'
version: 1.1
metadata:
  when_to_use:
  - Cuando ya existe scaffold o implementación inicial y se necesita validar que funciona.
  - Cuando se quiere diseñar la estrategia de pruebas del framework.
  - Cuando se necesita asegurar que el SDK, el core y los packs respetan sus contratos.
  - Cuando se debe validar guardrails, trazabilidad, memoria y seguridad antes de
    release.
  - Cuando se prepara un vertical slice o un release interno.
  phase:
  - quality
  layer:
  - implementation
  enforcement: mandatory
  depends_on:
  - framework-scaffold-implementation
  - framework-pack-design
  consumed_by:
  - framework-operations-evolution
  agent_roles:
  - delivery-agent
  - control-agent
  validation_profile: release-gate
  mcp_usage: none
---

# framework-qa-validation

## Propósito

Esta skill sirve para diseñar la validación del framework y sus componentes.  
Su función es definir cómo se verifica que la arquitectura, el scaffold y la implementación inicial cumplen los contratos, las reglas de seguridad, los comportamientos esperados y los criterios de aceptación establecidos.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Qué debe probarse en cada capa del framework?
2. ¿Qué contract tests aseguran que el SDK y el core no se rompen?
3. ¿Qué pruebas de integración y end-to-end son indispensables?
4. ¿Cómo se validan guardrails, trazabilidad, memoria y multitenencia?
5. ¿Qué evidencia se requiere para aceptar un vertical slice?
6. ¿Qué errores o regresiones deben bloquear un release?
7. ¿Cómo se define go/no-go para pasar de una fase a la siguiente?
8. ¿Qué pruebas deben correr automáticamente y cuáles pueden ser manuales?

## Relación con otras skills

- `framework-conception` aporta criterios funcionales de aceptación.
- `framework-architecture`, `framework-core-design`, `framework-data-memory-compliance`, `framework-security` y `framework-platform` aportan los contratos y comportamientos que deben validarse.
- `framework-scaffold-implementation` entrega el slice y el código base que esta skill debe verificar.
- `framework-operations-evolution` consume esta skill para definir gating de releases, regresiones y aprendizaje operativo.

## Qué debe hacer el agente cuando esta skill está activa

El agente debe:

1. Diseñar una estrategia de prueba por niveles.
2. Separar pruebas unitarias, contract, integración, end-to-end y validación operativa.
3. Definir qué contratos deben congelarse y versionarse.
4. Diseñar casos de prueba para packs, core, tools, seguridad y datos.
5. Incluir validación de guardrails, policies, tenant isolation y trazabilidad.
6. Definir criterios de aceptación claros y medibles.
7. Proponer evidencia mínima para aprobar un slice o release.
8. Diseñar checks automáticos para el pipeline.
9. Identificar qué debe detener el avance por riesgo.
10. Mantener la validación alineada con la arquitectura y el scaffold.

## Entradas esperadas

Esta skill asume que ya existe:
- arquitectura del framework;
- diseño del core;
- diseño de datos, seguridad y plataforma;
- scaffold o implementación inicial;
- al menos un vertical slice o caso de referencia.

Si falta esa base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase de QA y validación sí incluye:
- pruebas unitarias;
- contract tests;
- pruebas de integración;
- pruebas end-to-end;
- validación de guardrails;
- validación multi-tenant;
- validación de trazabilidad;
- validación de prompts/policies si aplica;
- criterios de aceptación;
- go/no-go;
- evidencia de release.

La fase de QA y validación no incluye todavía:
- operación continua de producción;
- observabilidad profunda de SRE a largo plazo;
- certificaciones externas ya obtenidas;
- gestión integral de calidad de toda la organización.

## Principios que siempre debe respetar

- Lo que no se prueba explícitamente se considera riesgoso.
- El contrato entre capas debe validarse antes que la lógica interna.
- Un slice end-to-end vale más que muchas pruebas aisladas sin integración.
- Guardrails, tenancy y trazabilidad son parte del comportamiento funcional.
- Las regresiones de contrato son más peligrosas que los bugs locales.
- Las pruebas deben automatizar lo repetible y reservar lo manual para juicio humano.
- La validación debe demostrar seguridad y utilidad, no solo compilación.
- El release solo avanza si los criterios están objetivamente cumplidos.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- qué se prueba y con qué nivel;
- qué contratos quedan protegidos;
- qué evidencia aprueba o bloquea un slice o release;
- qué criterios forman go/no-go.

Esta skill delega:
- la implementación del scaffold a `framework-scaffold-implementation`;
- la definición del producto a `framework-conception` y `framework-pack-design`;
- la operación continua del release a `framework-operations-evolution`;
- la ejecución automatizada de criterios de aceptación contra la implementación real (evidencia pass/fail/ambiguo por criterio) a `acceptance-test-automation`.

## Qué debe definir el diseño

### 1. Pirámide de pruebas
Definir:
- unit tests;
- integration tests;
- contract tests;
- end-to-end tests;
- regression tests;
- smoke tests;
- sanity checks;
- pruebas manuales o exploratorias.

### 2. Contract tests
Definir qué contratos deben quedar protegidos:
- SDK interno;
- core;
- router;
- tools;
- políticas;
- context payload;
- pack manifest;
- eventos o mensajes.

### 3. Validación por capa
Definir validaciones específicas para:
- interfaces de entrada;
- packs verticales;
- core agéntico;
- modelos LLM;
- memoria y datos;
- control y seguridad;
- infraestructura/pipeline.

### 4. Validación funcional de agentes
Definir:
- comportamiento esperado del agente;
- calidad de respuesta;
- uso correcto de tools;
- respeto de políticas;
- consistencia de pasos;
- recuperación ante fallos.

### 5. Validación de seguridad y control
Definir pruebas de:
- autenticación;
- autorización;
- RBAC;
- guardrails;
- bloqueo de acciones peligrosas;
- protección de secretos;
- no fuga de datos;
- trazabilidad completa.

### 6. Validación multi-tenant
Definir:
- aislamiento entre tenants;
- separación de datos;
- separación de contexto;
- no contaminación entre memorias;
- políticas por tenant;
- costos y límites por tenant.

### 7. Validación de observabilidad
Definir:
- existencia de traces;
- tags obligatorios;
- correlación request-model-tool-agent;
- logs de auditoría;
- métricas y latencia;
- visibilidad de costo;
- evidencia de eventos clave.

### 8. Vertical slice end-to-end
Definir un caso real que pruebe:
- request de entrada;
- resolución de tenant;
- invocación de pack;
- decisión del core;
- uso de modelo;
- tool call;
- memoria;
- seguridad;
- trazabilidad;
- respuesta final.

### 9. Criterios de aceptación
Definir:
- condiciones mínimas para aprobar;
- errores bloqueantes;
- umbrales cuantitativos si aplican;
- evidencia esperada;
- responsables de aprobación.

### 10. Go/No-Go
Definir:
- qué falla bloquea release;
- qué falla puede tolerarse temporalmente;
- quién toma la decisión;
- qué documentación o evidencia se exige.

## Preguntas guía

### 1. Sobre cobertura
- ¿Qué partes del framework no pueden quedar sin prueba?
- ¿Qué validación demuestra valor real y no solo que el sistema corre?
- ¿Qué se debe probar a nivel contrato versus a nivel comportamiento?

### 2. Sobre contratos
- ¿Qué interfaces o payloads no pueden cambiar sin aviso?
- ¿Qué versión del SDK se está validando?
- ¿Qué tool o policy no puede romperse sin afectar packs?

### 3. Sobre seguridad
- ¿Cómo demostramos que un tenant no ve datos de otro?
- ¿Cómo validamos que un guardrail realmente bloquea?
- ¿Cómo verificamos que secretos no se exponen?

### 4. Sobre agentes
- ¿Qué significa una buena ejecución del agente?
- ¿Qué outputs son válidos?
- ¿Qué loops, errores o alucinaciones deben detectar las pruebas?

### 5. Sobre observabilidad
- ¿Qué traces o logs deben aparecer sí o sí?
- ¿Qué tags permiten auditar y facturar?
- ¿Cómo se valida la correlación completa de una ejecución?

### 6. Sobre release
- ¿Qué evidencia se presenta para aprobar un slice?
- ¿Qué debe fallar para detener despliegue?
- ¿Qué puede arreglarse después sin bloquear el avance?

## Salidas esperadas de esta skill

Cuando esta skill responda, debe producir uno o varios de estos artefactos:

### A. Estrategia de pruebas por capa
- capa;
- tipo de prueba;
- objetivo;
- frecuencia.

### B. Catálogo de contract tests
- contrato;
- versión;
- escenario;
- criterio de éxito;
- riesgo mitigado.

### C. Matriz de validación de seguridad
- control;
- prueba;
- evidencia;
- severidad;
- resultado esperado.

### D. Casos de prueba multi-tenant
- caso;
- tenants involucrados;
- dato esperado;
- dato prohibido;
- evidencia.

### E. Validación del vertical slice
- paso;
- componente;
- expectativa;
- resultado real;
- observación.

### F. Criterios de aceptación
- criterio;
- umbral;
- evidencia;
- bloqueo si falla.

### G. Go/No-Go
- condición;
- estado;
- responsable;
- observación.

### H. Matriz de regresión
- área;
- riesgo;
- prueba mínima;
- frecuencia.

### I. Consumidores de la validación
- consumidor;
- evidencia consumida;
- decisión habilitada;
- riesgo si falta.

## Criterios de calidad

La skill debe evaluar el diseño usando estos criterios:

- cobertura suficiente de capas críticas;
- protección real del contrato;
- validación de seguridad y tenant isolation;
- evidencia operativa útil;
- automatización de lo repetible;
- claridad de criterios de aceptación;
- capacidad de detectar regresiones relevantes;
- validez del vertical slice como demostración del framework.

## Comportamiento esperado del agente

Cuando una propuesta sea solo lista de tests sin criterio, el agente debe volverla verificable.  
Cuando falte un contract test para una interfaz crítica, debe marcarlo como riesgo serio.  
Cuando un slice no valide seguridad, trazabilidad o multi-tenancy, debe considerarlo incompleto.  
Cuando haya demasiadas pruebas manuales para algo repetible, debe automatizarlo.
Cuando una discusión pase de validación a rediseño del framework, debe devolver la decisión a la skill de diseño correspondiente y mantener QA como función de evidencia y gating.

## Plantilla de respuesta recomendada

Usa esta estructura:

1. Objetivo de QA y validación.
2. Pirámide de pruebas.
3. Contract tests.
4. Validación por capa.
5. Validación de seguridad y multi-tenant.
6. Validación de trazabilidad y observabilidad.
7. Vertical slice end-to-end.
8. Criterios de aceptación y go/no-go.
9. Riesgos y brechas.
10. Roadmap de pruebas.

## Ejemplos de uso

### Ejemplo 1
Consulta: “Queremos validar el SDK del core sin romper packs.”

Respuesta esperada:
- contract tests del SDK;
- pruebas de compatibilidad;
- escenario con pack de referencia;
- gating en pipeline.

### Ejemplo 2
Consulta: “¿Cómo probamos que un tenant no ve datos de otro?”

Respuesta esperada:
- casos multi-tenant;
- validación de aislamiento en memoria, tools, logs y stores;
- evidencia negativa explícita.

### Ejemplo 3
Consulta: “Necesitamos aprobar un vertical slice para comité.”

Respuesta esperada:
- checklist de aceptación;
- pruebas funcionales, seguridad, trazabilidad y rendimiento mínimo;
- go/no-go con responsables.

## Checklist final de la skill

Antes de cerrar una respuesta, verificar:

- ¿Se definió una pirámide de pruebas?
- ¿Se protegieron los contratos críticos?
- ¿Se validó seguridad y multi-tenancy?
- ¿Se incluyó trazabilidad y observabilidad?
- ¿Existe un vertical slice end-to-end?
- ¿Hay criterios de aceptación claros?
- ¿Hay go/no-go explícito?
- ¿Se indicó qué evidencia consumen scaffold, operations o gobierno del cambio?
- ¿Se automatizó lo repetible?
- ¿Se identificaron riesgos y regresiones?
