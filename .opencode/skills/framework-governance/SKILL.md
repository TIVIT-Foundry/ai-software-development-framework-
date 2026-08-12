---
name: framework-governance
description: 'Usa esta skill para definir, aplicar y revisar las reglas maestras del
  framework de aplicaciones con agentes AI. Sirve para clasificar reglas obligatorias,
  estándares por defecto, decisiones variables y excepciones arquitectónicas antes
  de cualquier discovery o diseño detallado. Trigger: Cuando se inicia un nuevo proyecto,
  se necesita validar si una propuesta respeta el framework, o se discuten reglas
  obligatorias vs variables.'
version: 1.0
metadata:
  when_to_use:
  - Cuando se inicia un nuevo proyecto o pack vertical.
  - Cuando se necesita validar si una propuesta respeta el framework.
  - Cuando se discute si algo es obligatorio, estándar o variable.
  - Cuando se quiere revisar excepciones al blueprint.
  - Cuando se necesita alinear negocio, arquitectura, seguridad y plataforma.
  phase:
  - governance
  layer:
  - governance
  enforcement: mandatory
  depends_on:
  consumed_by:
  - framework-architecture
  - framework-data-memory-compliance
  - framework-discovery
  - framework-pack-design
  - framework-platform
  - framework-security
  - governance-constitution
  agent_roles:
  - control-agent
  - orchestrator-agent
  validation_profile: governance-review
  mcp_usage: none
---

# framework-governance

## Propósito

Esta skill establece la constitución del framework.  
Su función es asegurar que todas las soluciones construidas bajo este marco respeten los principios comunes de arquitectura, seguridad, operación y evolución, evitando que cada proyecto defina sus propias reglas desde cero.

Esta skill define restricciones y criterios de decisión. La skill `framework-architecture` toma esas restricciones y las traduce a diseño técnico concreto.

El framework busca construir aplicaciones de agentes con agilidad y escalabilidad mediante buenas prácticas de arquitectura, generando un portafolio de soluciones reutilizable, gobernable y consistente.

## Objetivo

Usa esta skill para responder estas preguntas antes de cualquier diseño detallado:

1. ¿Qué reglas son obligatorias para todos los proyectos?
2. ¿Qué reglas son estándares por defecto pero podrían cambiar con justificación?
3. ¿Qué decisiones son variables por cliente, sector o vertical?
4. ¿Qué excepciones necesitan aprobación explícita?
5. ¿Cómo validamos que una propuesta sigue alineada con el framework?

## Relación con otras skills

- `framework-governance` decide principios, reglas y excepciones.
- `framework-architecture` convierte esas reglas en estructura técnica y contratos entre capas.
- `framework-security`, `framework-platform` y `framework-operations-evolution` aplican y endurecen esas reglas en controles y operación.
- `framework-discovery`, `framework-conception` y `framework-pack-design` no deben redefinir reglas base del framework; deben operar dentro de ellas.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- qué principios son obligatorios;
- qué estándares aplican por defecto;
- qué decisiones son variables;
- qué propuestas requieren excepción;
- qué baseline deben respetar las demás skills.

Esta skill delega:
- el diseño técnico a `framework-architecture` y las skills de capa;
- la definición del vertical y del producto a discovery, conception y pack-design;
- la implementación y validación a scaffold, QA y operations.

## Principios rectores

Toda decisión debe respetar los siguientes principios:

- Arquitectura modular en 7 capas, donde cada capa cumple una función específica y es reemplazable de forma independiente.
- Principio Build vs Buy: construir lo diferenciador comercial e integrar lo commodity técnico.
- Multi-tenant desde el ingreso: ningún request puede procesarse sin tenant válido.
- Aislamiento estricto entre clientes: no mezclar datos, memoria ni conocimiento operativo entre tenants.
- Core model-agnostic: ningún pack debe quedar acoplado a un proveedor o modelo LLM específico.
- Observabilidad y trazabilidad end-to-end como capacidad nativa.
- Seguridad, guardrails y secretos como parte del diseño base, no como agregado posterior.
- Portabilidad de la lógica propia sobre infraestructura Kubernetes-native.

## Qué debe hacer el agente cuando esta skill está activa

El agente debe:

1. Identificar si la consulta pertenece a gobierno del framework o a diseño/implementación.
2. Clasificar cada decisión en una de estas categorías:
   - Obligatoria
   - Estándar por defecto
   - Variable
   - Excepción
3. Mapear cualquier propuesta relevante a las 7 capas del framework.
4. Señalar explícitamente cuando una propuesta viola un principio rector.
5. No recomendar tecnologías o patrones que rompan multitenencia, aislamiento, model-agnostic, trazabilidad o portabilidad sin marcarlo como excepción.
6. Pedir justificación si el usuario propone desviarse del blueprint.
7. Mantener separación entre:
   - reglas de framework,
   - decisiones de solución,
   - decisiones de proveedor,
   - personalización por tenant.
8. **Pedir explícitamente (HITL) el nombre del ingeniero a cargo / owner del sistema**
   antes de asentar aprobadores de excepciones, decisiones arquitectónicas o deuda.
   Nunca inferir el owner del proyecto desde el autor del framework (p. ej. AGENTS.md):
   el autor del framework NO es el owner de los proyectos construidos con él.
   Si el dato no se provee, marcar `Aprobador: [PENDIENTE — confirmar con owner]`.
9. Registrar la deuda técnica y de seguridad pendiente en el artefacto de governance
   (sección "Deuda técnica y deuda de seguridad") con owner y fecha de revisión —
   nunca solo en el state del workflow (`.workflow/state.json`), que puede perderse.

## Reglas obligatorias

Estas reglas son no negociables salvo excepción aprobada.

### 1. Estructura del framework
- Toda solución debe mapearse a las 7 capas del framework.
- Cada capa debe mantener una responsabilidad clara y separable.

### 2. Entrada y control de acceso
- Todo request debe entrar por la capa de interfaces de entrada.
- El tenant_id debe resolverse antes de cualquier procesamiento.
- Deben existir autenticación, autorización, normalización de request y controles de rate limiting/protección.

### 3. Multi-tenancy y aislamiento
- Ningún componente puede mezclar datos de distintos tenants.
- La separación de tenants debe existir en memoria, datos, políticas y operación.

### 4. Core y evolución
- Debe existir un contrato estable entre packs y core.
- El core debe soportar routing por costo, latencia y sensibilidad.
- Los packs no deben acoplarse directamente a un único modelo LLM.

### 5. Seguridad y auditoría
- Toda interacción relevante del agente debe ser trazable y auditable.
- Deben existir guardrails y gestión de secretos.
- Debe existir control de políticas de acceso y uso.
- Toda deuda de seguridad conocida (denylist pendiente, rate-limit ausente, headers
  faltantes, dependencias vulnerables, etc.) debe registrarse en el artefacto de
  governance (ver "Deuda técnica y deuda de seguridad") con owner y fecha de revisión —
  no solo en el state del workflow.

### 6. Portabilidad e infraestructura
- La lógica propia del framework debe ser portable y correr sobre Kubernetes estándar.
- La solución debe contemplar observabilidad, despliegue y operación multi-tenant.

## Estándares por defecto

Estas reglas aplican por defecto, pero pueden cambiar con justificación:

- LangGraph como motor de orquestación.
- MCP como estándar para catálogo de herramientas.
- OpenTelemetry para trazabilidad por request.
- Langfuse para trazas y evaluaciones.
- Vault + KMS para secretos.
- Qdrant, Neo4j o Spanner Graph y PostgreSQL como stack de memoria y datos de referencia.
- Temporal para workflows largos.
- Kubernetes + GitOps + observabilidad de infraestructura como baseline operativo.

## Variables permitidas

Estas decisiones pueden cambiar por proyecto, cliente o sector:

- Proveedor cloud o entorno on-premise.
- API Gateway e Identity Provider específicos.
- Modelos LLM activos por tenant.
- Nivel de guardrails por industria.
- Packs verticales priorizados.
- Nivel de memoria organizacional contratado.
- Estrategia de costos, escalado y observabilidad según tier de cliente.

## Excepciones

Se considera excepción cualquier propuesta que:

- omita una de las 7 capas;
- procese requests sin tenant resuelto;
- mezcle datos o memoria entre tenants;
- acople un pack a un único LLM o proveedor;
- elimine trazabilidad o auditoría;
- quite guardrails o gestión de secretos;
- haga que la lógica propia dependa de una nube o plataforma no portable.

Toda excepción debe documentarse con:
- motivo;
- alcance;
- riesgo;
- mitigación;
- duración;
- fecha de revisión o expiración;
- responsable de aprobación.

## Deuda técnica y deuda de seguridad

La deuda conocida y aceptada (técnica o de seguridad) no es una excepción aprobada,
pero tampoco puede quedar solo en el state del workflow (`.workflow/state.json`), que
puede perderse o no leerse en el siguiente ciclo. Debe registrarse en el artefacto de
governance del proyecto:

| Campo | Descripción |
|---|---|
| ID | `DEUDA-001` correlativo |
| Tipo | `seguridad` \| `técnica` \| `calidad` |
| Descripción | Qué queda pendiente y por qué se acepta hoy |
| Riesgo si no se paga | Impacto concreto (ej. "tokens accesibles vía denylist sin rate-limit") |
| Mitigación temporal | Control parcial aplicado mientras tanto |
| Owner | Persona responsable (pedida por HITL — ver §"Qué debe hacer el agente") |
| Fecha de revisión | Cuándo se revisa/paga (deuda de seguridad: máx. 30 días) |

Reglas:
- Deuda de seguridad **nunca** se cierra sin owner + fecha de revisión.
- Al pagar la deuda, actualizar el artefacto (estado `pagada`) y registrar el fix.
- Las observaciones de `review-adversarial` y `framework-qa-validation` que queden
  pendientes se registran aquí, no solo en el resumen del bundle.

## Salidas esperadas de esta skill

Cuando esta skill responda, debe devolver uno o varios de estos formatos:

### A. Matriz de gobierno
| Regla | Categoría | Aplica a | Riesgo si no se cumple |
|---|---|---|---|

### B. Revisión de propuesta
- Cumple
- No cumple
- Requiere excepción
- Información faltante

### C. Checklist arquitectónico
- capas cubiertas;
- principios respetados;
- excepciones abiertas;
- decisiones pendientes.

### D. Dictamen
- Aprobado
- Aprobado con observaciones
- Requiere cambios
- Rechazado por violar principios base

### E. Registro de excepciones
- excepción;
- principio afectado;
- justificación;
- mitigación;
- fecha de revisión;
- aprobador.

### F. Consumidores del gobierno del framework
- consumidor;
- regla o excepción consumida;
- decisión habilitada;
- riesgo si falta.

## Preguntas que esta skill debe hacer si falta contexto

Antes de validar una solución, preguntar:

- ¿Qué tipo de proyecto es: framework base, pack vertical, PoC, MVP o solución enterprise?
- **¿Quién es el ingeniero a cargo / owner del sistema y quién aprueba las decisiones
  arquitectónicas?** (HITL obligatorio — no inferir del autor del framework)
- ¿Es single-tenant temporal o multi-tenant desde el inicio?
- ¿Qué vertical o dominio se está atendiendo?
- ¿Qué requisitos regulatorios existen?
- ¿Qué partes quieren construir y cuáles integrar?
- ¿Qué excepciones están considerando?

## Comportamiento esperado del agente

Cuando el usuario pida opinión, el agente no debe responder solo con preferencia técnica.  
Debe responder desde gobierno del framework:
- primero los principios,
- luego la clasificación obligatoria/default/variable,
- luego los riesgos,
- finalmente la recomendación.

Cuando el caso pertenezca realmente a diseño técnico, el agente debe usar governance para fijar restricciones y luego remitir el aterrizaje a `framework-architecture` u otra skill especializada.

## Plantilla de respuesta recomendada

Usa esta estructura:

1. Contexto de la decisión.
2. Regla del framework aplicable.
3. Clasificación:
   - Obligatorio
   - Estándar por defecto
   - Variable
   - Excepción
4. Impacto arquitectónico.
5. Recomendación.
6. Próximo paso de validación.

## Ejemplos de uso

### Ejemplo 1
Consulta: “¿Podemos hacer un pack conectado solo a OpenAI?”

Respuesta esperada:
- No como diseño base.
- El framework exige model-agnostic en el core.
- OpenAI puede ser proveedor inicial, pero no dependencia rígida del pack.

### Ejemplo 2
Consulta: “¿Podemos evitar tenant_id en el MVP?”

Respuesta esperada:
- No, salvo excepción explícita.
- El framework exige multi-tenant desde el ingress como regla estructural.

### Ejemplo 3
Consulta: “¿Podemos usar otro motor distinto de LangGraph?”

Respuesta esperada:
- Sí, pero como variación del estándar por defecto.
- Debe justificarse compatibilidad con orquestación, HITL, recuperación de fallos y contrato del core.

## Checklist final de la skill

Antes de cerrar una respuesta, verificar:

- ¿Se distinguió claramente entre obligatorio, estándar, variable y excepción?
- ¿Se mapearon las implicancias en las capas relevantes?
- ¿Se protegieron multitenencia, aislamiento y seguridad?
- ¿Se respetó el principio Build vs Buy?
- ¿Se evitó lock-in innecesario?
- ¿Se indicó si la siguiente decisión pertenece a architecture, security, platform u operations?
- ¿Se explicó el riesgo de desviarse del framework?
- ¿Se dejó claro el próximo paso?
