---
name: framework-security
description: 'Usa esta skill para diseñar la capa de seguridad y control del framework.
  Sirve para definir autorización, RBAC, políticas, guardrails, gestión de secretos,
  trazabilidad, auditoría, control de tool calling, límites de autonomía, presupuestos
  y facturación granular multi-tenant. Trigger: Cuando se necesita diseñar la capa
  de seguridad: autorización, RBAC, guardrails, secretos y auditoría multi-tenant.'
version: 1.0
metadata:
  when_to_use:
  - Cuando se necesita diseñar la capa 6 del framework.
  - Cuando se quiere definir quién puede hacer qué dentro del sistema.
  - Cuando se requiere controlar outputs, herramientas, decisiones y acciones críticas.
  - Cuando se debe proteger credenciales, secretos y accesos a sistemas del cliente.
  - Cuando se necesita preparar la solución para clientes enterprise o sectores regulados.
  phase:
  - architecture
  layer:
  - design
  enforcement: mandatory
  depends_on:
  - framework-architecture
  - framework-governance
  consumed_by:
  - framework-platform
  - framework-scaffold-implementation
  agent_roles:
  - control-agent
  - delivery-agent
  - design-agent
  validation_profile: security-review
  mcp_usage: governed
---

# framework-security

## Propósito

Esta skill sirve para diseñar los controles que hacen segura, auditable y gobernable la operación de agentes.  
Su función es definir cómo se autorizan acciones, cómo se protegen credenciales, cómo se aplican guardrails, cómo se trazan las decisiones y cómo se controlan el riesgo, el presupuesto y la exposición por tenant.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Quién puede invocar qué dentro del framework?
2. ¿Qué acciones requieren autorización, validación adicional o bloqueo?
3. ¿Qué guardrails deben aplicarse a inputs, razonamiento, tool calls y outputs?
4. ¿Cómo se protegen secretos y credenciales de cliente?
5. ¿Qué debe quedar auditado y con qué nivel de detalle?
6. ¿Qué políticas cambian por tenant, vertical o industria?
7. ¿Cómo se controla el presupuesto, consumo y facturación granular?
8. ¿Cómo se diseñan controles suficientes para vender a sectores regulados?

## Relación con otras skills

- `framework-governance` define principios obligatorios y excepciones que esta skill convierte en controles verificables.
- `framework-architecture` delimita dónde deben existir controles y qué componentes quedan bajo protección.
- `framework-data-memory-compliance` define sensibilidad, stores y retención sobre los que esta skill aplica acceso, auditoría y protección.
- `framework-platform` provee secretos, runtime, observabilidad y enforcement operativo que esta skill debe exigir.
- `framework-operations-evolution` usa esta skill para responder incidentes, cambios de política y evidencias de auditoría.

## Qué debe hacer el agente cuando esta skill está activa

El agente debe:

1. Diseñar controles de autorización para usuarios, servicios, packs, agentes y tools.
2. Definir RBAC y políticas contextuales.
3. Diseñar guardrails en múltiples etapas del flujo.
4. Definir controles para acciones de lectura, escritura y acción crítica.
5. Diseñar gestión segura de secretos y credenciales.
6. Definir trazabilidad y auditoría inviolable.
7. Incorporar políticas por tenant, por vertical y por nivel regulatorio.
8. Diseñar control de presupuestos, límites y facturación por consumo.
9. Separar claramente seguridad del framework frente a seguridad del sistema integrado del cliente.
10. Proponer controles compatibles con multi-tenancy y operación real.

## Entradas esperadas

Esta skill asume que ya existe:
- gobierno del framework;
- arquitectura general;
- diseño del core;
- diseño de datos y memoria;
- conocimiento de vertical y sensibilidad del caso de uso.

Si esta información no existe, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase de seguridad y control sí incluye:
- autenticación y autorización funcionales;
- RBAC;
- políticas contextuales;
- guardrails;
- gestión de secretos;
- trazabilidad;
- auditoría;
- logs inmutables;
- control de tool calling;
- límites de autonomía;
- control de presupuesto y billing;
- configuración por tenant.

La fase de seguridad y control no incluye todavía:
- certificación formal ya obtenida;
- SOC corporativo completo fuera del framework;
- hardening de infraestructura de bajo nivel que pertenece más a plataforma.

## Principios que siempre debe respetar

- Ninguna acción relevante debe ocurrir sin identidad, contexto y tenant válidos.
- Todo control debe ser auditable.
- Las acciones más riesgosas requieren políticas más estrictas.
- Secretos nunca deben exponerse a agentes ni usuarios fuera de su necesidad real.
- Guardrails deben existir antes y después de los modelos.
- Los controles deben poder variar por tenant y por sector.
- La trazabilidad debe ser suficiente para reconstruir una decisión.
- Seguridad y compliance son parte del producto, no un extra.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- identidad, autorización y RBAC;
- guardrails por etapa;
- clasificación de acciones y tools;
- gestión de secretos a nivel de política y control;
- auditoría, presupuestos y límites de autonomía.

Esta skill delega:
- topología operativa y mecanismos concretos de despliegue a `framework-platform`;
- taxonomía, retención y source of truth a `framework-data-memory-compliance`;
- lógica de negocio del vertical a `framework-pack-design`;
- contrato de ejecución del runtime a `framework-core-design`.

## Qué debe definir el diseño

### 1. Modelo de identidad y autorización
Definir:
- identidades humanas;
- identidades de servicio;
- scopes;
- roles;
- permisos;
- contexto mínimo de autorización;
- vínculo con tenant, pack, agente y tool.

### 2. RBAC y políticas contextuales
Definir:
- roles base;
- permisos por pack;
- permisos por agente;
- permisos por herramienta;
- restricciones por horario, presupuesto, entorno o criticidad;
- evaluación con OPA o equivalente.

### 3. Clasificación de acciones
Definir al menos:
- read-only;
- write;
- action with external impact;
- privileged action;
- irreversible action.

Cada categoría debe tener controles y niveles de autorización distintos.

### 4. Guardrails
Definir guardrails para:
- input;
- prompt injection;
- jailbreak;
- toxicidad;
- PII/PHI;
- outputs inválidos;
- outputs fuera de política;
- tool calls peligrosas;
- acciones autónomas no autorizadas.

También definir:
- bloqueo;
- sanitización;
- redacción;
- revisión humana;
- fallback seguro.

### 5. Gestión de secretos
Definir:
- almacenamiento seguro;
- acceso por mínimo privilegio;
- rotación;
- cifrado;
- auditoría de uso;
- segregación por tenant;
- uso indirecto por tools sin exponer el secreto al modelo.

### 6. Trazabilidad y auditoría
Definir qué debe registrarse:
- request;
- tenant;
- usuario o servicio;
- pack;
- agente;
- modelo;
- tool call;
- decisión del router;
- guardrail aplicado;
- output final;
- costo;
- latencia;
- autorización evaluada.

También definir:
- retención;
- inmutabilidad;
- nivel de detalle;
- eventos obligatorios para auditoría.

### 7. Control de tools y acciones críticas
Definir:
- clasificación de tools;
- allowlist por pack/tenant;
- validación de inputs;
- confirmación previa;
- idempotencia si aplica;
- doble validación o HITL para acciones críticas;
- rollback o compensación cuando sea posible.

### 8. Límites de autonomía
Definir:
- qué puede hacer el agente solo;
- qué puede recomendar;
- qué debe escalar a humano;
- umbrales por riesgo;
- umbrales por costo;
- umbrales por tipo de tenant o sector.

### 9. Presupuesto, consumo y billing
Definir:
- medición por tokens;
- medición por modelo;
- medición por tool;
- medición por almacenamiento;
- reporting por tenant;
- límites de gasto;
- alertas;
- throttling;
- políticas de suspensión o degradación.

### 10. Configuración por tenant y por sector
Definir:
- guardrails más estrictos o flexibles;
- herramientas habilitadas;
- modelos permitidos;
- límites de autonomía;
- umbrales de presupuesto;
- requisitos especiales para banca, salud, gobierno, retail, etc.

## Preguntas guía

### 1. Sobre acceso
- ¿Quiénes son los actores del sistema?
- ¿Qué permisos necesitan realmente?
- ¿Qué acciones deberían estar prohibidas por defecto?
- ¿Qué permisos son temporales o excepcionales?

### 2. Sobre guardrails
- ¿Qué riesgos del caso de uso son más importantes: fuga de datos, alucinación, acción errónea, toxicidad, incumplimiento?
- ¿Dónde conviene bloquear y dónde conviene revisar?
- ¿Qué outputs nunca deberían salir sin validación humana?

### 3. Sobre tools
- ¿Qué tools solo leen y cuáles modifican sistemas externos?
- ¿Qué tool calls requieren aprobación?
- ¿Qué errores de tool podrían generar impacto severo?

### 4. Sobre secretos
- ¿Qué credenciales maneja el framework?
- ¿Quién puede usarlas y cómo?
- ¿Cómo se evita que el modelo vea o exponga secretos?

### 5. Sobre auditoría
- ¿Qué eventos necesita revisar un auditor o cliente enterprise?
- ¿Qué nivel de detalle se necesita para reconstruir una decisión?
- ¿Qué logs deben ser inmutables?

### 6. Sobre costo y control
- ¿Qué límites financieros o de consumo deben existir?
- ¿Qué pasa si un tenant supera su presupuesto?
- ¿Cómo se reporta el uso por pack, agente, modelo y herramienta?

### 7. Sobre regulación
- ¿Qué industrias requieren políticas más duras?
- ¿Qué acciones quedan restringidas por norma o contrato?
- ¿Qué evidencias debe poder exportar el sistema?

## Salidas esperadas de esta skill

Cuando esta skill responda, debe producir uno o varios de estos artefactos:

### A. Modelo de acceso
- actor;
- rol;
- permiso;
- recurso;
- restricción;
- observaciones.

### B. Matriz RBAC y políticas
- pack;
- agente;
- tool;
- acción;
- permitido/denegado/condicional;
- política aplicable.

### C. Catálogo de guardrails
- riesgo;
- etapa;
- control;
- acción al detectar;
- severidad.

### D. Política de secretos
- secreto;
- uso;
- ubicación;
- acceso permitido;
- rotación;
- logging.

### E. Estrategia de auditoría
- evento;
- nivel de detalle;
- retención;
- inmutabilidad;
- uso previsto.

### F. Política de acciones críticas
- acción;
- criticidad;
- autorización requerida;
- HITL;
- rollback o compensación.

### G. Diseño de control de consumo y billing
- métrica;
- unidad;
- límite;
- alerta;
- acción al exceder.

### H. Configuración por tenant
- control;
- nivel;
- alcance;
- justificación.

### I. Riesgos y mitigaciones
- riesgo;
- impacto;
- probabilidad;
- mitigación;
- residual.

### J. Consumidores del diseño de seguridad
- consumidor;
- control consumido;
- uso esperado;
- validación necesaria.

## Criterios de calidad

La skill debe evaluar el diseño usando estos criterios:

- autorización consistente y mínima;
- guardrails efectivos y no decorativos;
- secretos realmente protegidos;
- trazabilidad suficiente para auditoría;
- separación correcta por tenant;
- control claro de acciones críticas;
- medición granular utilizable comercialmente;
- configurabilidad por sector y tenant;
- equilibrio entre seguridad, operación y experiencia.

## Comportamiento esperado del agente

Cuando una propuesta “confíe” en el agente sin controles, el agente debe endurecerla.  
Cuando una acción modifique sistemas externos, debe elevar criticidad y revisar HITL.  
Cuando un control solo exista en documentación y no en enforcement técnico, debe marcarlo como insuficiente.  
Cuando el diseño genere demasiada fricción para un MVP, debe simplificar sin renunciar a los controles esenciales.
Cuando una decisión sea de taxonomía de datos o de arquitectura operativa del runtime, debe separar el control de seguridad del detalle que corresponde a data o platform.

## Plantilla de respuesta recomendada

Usa esta estructura:

1. Objetivo de seguridad y control.
2. Modelo de identidad y autorización.
3. RBAC y políticas contextuales.
4. Guardrails por etapa.
5. Secretos y credenciales.
6. Trazabilidad y auditoría.
7. Control de tools y acciones críticas.
8. Presupuesto, consumo y billing.
9. Configuración por tenant y por sector.
10. Riesgos y decisiones pendientes.

## Ejemplos de uso

### Ejemplo 1
Consulta: “Diseña seguridad y control para un pack SOC.”

Respuesta esperada:
- clasificar tools y acciones de alto impacto;
- endurecer guardrails;
- exigir trazabilidad, HITL y control estricto por tenant.

### Ejemplo 2
Consulta: “Queremos permitir acciones automáticas en Customer Engagement.”

Respuesta esperada:
- separar acciones de bajo riesgo frente a acciones irreversibles;
- definir límites de autonomía;
- introducir aprobación cuando el impacto lo requiera.

### Ejemplo 3
Consulta: “¿Cómo hacemos monetización granular por tenant?”

Respuesta esperada:
- medir tokens, llamadas, tools, storage y SLA;
- asociar uso a tenant, pack, agente y modelo;
- activar alertas y políticas de límite.

## Checklist final de la skill

Antes de cerrar una respuesta, verificar:

- ¿Se definió identidad, autorización y RBAC?
- ¿Se definieron guardrails reales por etapa?
- ¿Se protegieron secretos y credenciales?
- ¿Se diseñó auditoría suficiente e inmutable?
- ¿Se clasificaron tools y acciones críticas?
- ¿Se resolvieron límites de autonomía?
- ¿Se definió medición y billing granular?
- ¿Se contempló configuración por tenant y sector?
- ¿Se distinguió qué parte se implementa en platform, data y core?
- ¿Se documentaron riesgos y mitigaciones?
