---
name: framework-core-design
description: 'Usa esta skill para diseñar el core agéntico reusable del framework.
  Sirve para definir el SDK interno, el contrato entre packs y core, la orquestación,
  el router model-agnostic, el catálogo MCP de herramientas, el manejo de estado,
  HITL, validación, fallback y trazabilidad. Trigger: Cuando se necesita definir o
  revisar el core agéntico reusable: SDK, orquestación, router, MCP y trazabilidad.'
version: 1.0
metadata:
  when_to_use:
  - Cuando se necesita definir o revisar la capa 3 del framework.
  - Cuando se quiere diseñar el motor común que usarán todos los packs.
  - Cuando se requiere un contrato estable entre packs y core.
  - Cuando se necesita definir router, tools, orquestación y ejecución agéntica.
  - Cuando se quiere separar claramente capacidades del core frente a capacidades
    del pack.
  phase:
  - architecture
  layer:
  - design
  enforcement: mandatory
  depends_on:
  - framework-architecture
  consumed_by:
  - framework-scaffold-implementation
  agent_roles:
  - design-agent
  - control-agent
  validation_profile: architecture-consistency, skill-contract
  mcp_usage: governed
---

# framework-core-design

## Propósito

Esta skill sirve para diseñar el core agéntico como motor transversal del framework.  
Su función es definir cómo los packs invocan un runtime común para coordinar agentes, herramientas, modelos, memoria y validaciones sin acoplarse a implementaciones internas ni a proveedores específicos.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Qué responsabilidades pertenecen al core y no a los packs?
2. ¿Qué contrato estable expone el core hacia los packs?
3. ¿Cómo se orquesta un flujo agéntico end-to-end?
4. ¿Cómo se selecciona el modelo adecuado por paso?
5. ¿Cómo se exponen las herramientas de forma uniforme?
6. ¿Cómo se manejan estado, contexto y tenant durante la ejecución?
7. ¿Cómo se resuelven validación, fallback, retries y human-in-the-loop?
8. ¿Cómo se versiona el core sin romper compatibilidad con los packs?

## Relación con otras skills

- `framework-architecture` define los límites, contratos principales y dependencias que el core debe implementar.
- `framework-pack-design` define qué conocimiento, prompts y runbooks viven fuera del core.
- `framework-security`, `framework-data-memory-compliance` y `framework-platform` completan controles, datos y runtime que el core debe consumir sin absorber como lógica propia.
- `framework-scaffold-implementation` y `framework-qa-validation` consumen esta skill para materializar y verificar el contrato pack-core.

## Qué debe hacer el agente cuando esta skill está activa

El agente debe:

1. Delimitar claramente qué pertenece al core y qué pertenece al pack.
2. Diseñar el SDK interno como contrato estable de largo plazo.
3. Definir el runtime de orquestación y sus estados principales.
4. Diseñar el router model-agnostic con políticas por tenant.
5. Diseñar el catálogo de herramientas y su interfaz uniforme.
6. Definir cómo fluye el contexto: tenant, sesión, agente, presupuesto, seguridad y trazas.
7. Incorporar validación, guardrails técnicos, retries, fallback y HITL como capacidades nativas.
8. Diseñar el tracing del razonamiento, llamadas a tools y uso de modelos.
9. Proponer versionado y backward compatibility.
10. Evitar que los packs dependan de detalles internos del core.

## Entradas esperadas

Esta skill asume que ya existe:
- gobierno del framework;
- definición arquitectónica general;
- diseño preliminar de packs o necesidades comunes;
- principios de multi-tenancy y seguridad.

Si no existe esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase de diseño del core agéntico sí incluye:
- contrato pack-core;
- SDK interno;
- runtime de orquestación;
- router de modelos;
- interfaz de tools;
- integración con MCP;
- manejo de estado y contexto;
- políticas de ejecución;
- soporte de HITL;
- fallback y retries;
- trazabilidad del razonamiento;
- versionado y compatibilidad.

La fase de diseño del core agéntico no incluye todavía:
- diseño específico de un pack vertical;
- definición profunda de infraestructura física;
- configuración final de seguridad corporativa;
- implementación de todas las tools del negocio.

## Principios que siempre debe respetar

- El core debe sostener años de evolución sin romper packs.
- El core debe ser model-agnostic por diseño.
- El core debe exponer un contrato estable, explícito y versionado.
- El core debe desacoplar pack, modelo, tool y ejecución.
- El core debe propagar contexto multi-tenant de extremo a extremo.
- El core debe registrar cada decisión, llamada y resultado.
- El core debe soportar tanto automatización como human-in-the-loop.
- El core debe integrar estándares maduros cuando no haya valor en reescribirlos.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- el contrato pack-core y el SDK interno;
- el runtime de orquestación;
- el router model-agnostic;
- la interfaz uniforme de tools;
- el manejo de contexto, estado, fallback y HITL;
- la trazabilidad técnica del flujo agéntico.

Esta skill no debe absorber:
- prompts, runbooks o reglas de dominio del pack;
- políticas corporativas completas de seguridad;
- diseño detallado de stores, retención o residencia de datos;
- topología operativa de plataforma e infraestructura.

## Qué debe definir el diseño del core

### 1. Responsabilidad del core
Definir qué le corresponde al core:
- orquestación;
- ejecución de agentes;
- router de modelos;
- catálogo uniforme de tools;
- manejo de estado;
- validación;
- fallback;
- HITL;
- tracing;
- contrato con memoria y control.

También debe definir explícitamente qué no le corresponde:
- prompts específicos del vertical;
- runbooks de dominio;
- lógica de negocio particular de cada pack.

### 2. SDK interno
Definir:
- interfaz que usa el pack para declarar agentes, tareas, tools y políticas;
- primitivas del SDK;
- objetos base;
- contratos de entrada y salida;
- hooks o extensibilidad;
- versionado semántico;
- reglas de backward compatibility.

### 3. Runtime de orquestación
Definir:
- estados del flujo;
- pasos de planificación;
- ejecución;
- validación;
- reintento;
- escalamiento a humano;
- finalización;
- recuperación ante fallos;
- control de ciclos o loops.

### 4. Router model-agnostic
Definir:
- input del router;
- criterios de decisión;
- políticas por tenant;
- costo;
- latencia;
- sensibilidad;
- tipo de tarea;
- fallback chain;
- límites presupuestales;
- trazabilidad de la decisión.

### 5. Catálogo de herramientas
Definir:
- interfaz común de tools;
- descubrimiento y registro;
- permisos de uso;
- validación de inputs y outputs;
- clasificación por criticidad;
- manejo de errores;
- exposición vía MCP o equivalente.

### 6. Contexto y estado
Definir:
- tenant_id;
- session_id;
- correlation_id;
- actor o usuario;
- agente activo;
- presupuesto;
- políticas aplicables;
- memoria disponible;
- herramientas habilitadas;
- estado conversacional y operativo.

### 7. Validación y control de ejecución
Definir:
- validación estructural de inputs;
- validación de outputs;
- chequeos previos a tool call;
- chequeos posteriores;
- detección de errores recuperables;
- reglas para retries;
- condiciones de fallback;
- condiciones de stop.

### 8. Human-in-the-loop
Definir:
- puntos de pausa;
- criterios de escalamiento;
- payload de revisión humana;
- reanudación del flujo;
- auditoría del handoff;
- límites de autonomía por tipo de acción.

### 9. Trazabilidad
Definir:
- qué eventos se registran;
- nivel de detalle;
- trazas por request, agente, tool y modelo;
- costo por paso;
- latencia;
- decisiones del router;
- outputs validados y rechazados.

### 10. Evolución del core
Definir:
- política de versionado;
- compatibilidad entre versiones;
- estrategia de deprecación;
- pruebas de compatibilidad para packs;
- cómo introducir nuevas capacidades sin romper integraciones previas.

## Preguntas guía

### 1. Sobre responsabilidades
- ¿Qué problema transversal resuelve el core para todos los packs?
- ¿Qué cosas no deberían implementarse repetidamente en cada pack?
- ¿Qué elementos deben quedar fuera del core para evitar sobrediseño?

### 2. Sobre el contrato
- ¿Qué necesita declarar un pack para ejecutarse sobre el core?
- ¿Qué garantiza el core al pack?
- ¿Qué objetos o estructuras forman el contrato mínimo?

### 3. Sobre la orquestación
- ¿Qué tipos de flujo debe soportar el runtime?
- ¿Qué estados son obligatorios?
- ¿Cómo se recupera una ejecución fallida?
- ¿Cómo se evita un loop infinito o una cadena de decisiones erróneas?

### 4. Sobre el router
- ¿Qué información necesita el router para elegir modelo?
- ¿Cuándo se privilegia costo, latencia o calidad?
- ¿Cómo se manejan políticas específicas por tenant?
- ¿Cómo se cae elegantemente a otro modelo?

### 5. Sobre tools
- ¿Qué formato común tendrá una tool?
- ¿Cómo se autorizan tools sensibles?
- ¿Cómo se distinguen tools read-only, write o critical action?
- ¿Cómo se comunican errores o resultados ambiguos?

### 6. Sobre contexto
- ¿Qué contexto mínimo debe portar toda ejecución?
- ¿Qué parte vive en memoria transitoria y cuál en persistencia?
- ¿Cómo se propaga el tenant sin pérdida?

### 7. Sobre HITL
- ¿Qué acciones requieren revisión humana sí o sí?
- ¿Qué información se presenta al humano revisor?
- ¿Cómo reanuda el flujo una vez aprobada o rechazada la acción?

### 8. Sobre evolución
- ¿Cómo evitamos que una mejora del core rompa packs existentes?
- ¿Qué parte del contrato puede extenderse?
- ¿Qué parte debe permanecer estable por años?

## Salidas esperadas de esta skill

Cuando esta skill responda, debe producir uno o varios de estos artefactos:

### A. Mapa de responsabilidades del core
- responsabilidad;
- descripción;
- pertenece al core / no pertenece al core;
- observaciones.

### B. Diseño del SDK interno
- primitivas;
- interfaces;
- objetos base;
- contratos;
- hooks;
- versionado.

### C. Flujo del runtime agéntico
- estados;
- transiciones;
- entradas;
- salidas;
- errores;
- retries;
- pausas HITL.

### D. Diseño del router de modelos
- entradas;
- políticas;
- criterios;
- fallback;
- límites;
- trazabilidad.

### E. Diseño del catálogo de tools
- interfaz;
- registro;
- permisos;
- clasificación;
- errores;
- observabilidad.

### F. Modelo de contexto y estado
- campos obligatorios;
- ciclo de vida;
- persistencia;
- propagación entre capas.

### G. Diseño de tracing
- eventos;
- tags;
- métricas;
- correlación;
- auditoría técnica.

### H. ADRs del core
- decisión;
- contexto;
- alternativas;
- opción elegida;
- trade-off.

### I. Consumidores del diseño del core
- consumidor;
- artefacto consumido;
- uso esperado;
- validación necesaria.

## Criterios de calidad del core

La skill debe evaluar el diseño del core usando estos criterios:

- estabilidad del contrato;
- desacoplamiento entre pack y ejecución interna;
- independencia frente a proveedores de modelos;
- soporte real de multi-tenancy;
- control del estado y recuperación;
- seguridad operativa de tool calling;
- trazabilidad profunda;
- extensibilidad sin ruptura;
- simplicidad suficiente para MVP y solidez para evolución futura.

## Comportamiento esperado del agente

Cuando una propuesta meta lógica de dominio dentro del core, el agente debe devolverla al pack.  
Cuando un diseño acople el core a un modelo o proveedor, debe marcarlo como anti-patrón.  
Cuando el runtime se vuelva excesivamente complejo para el MVP, debe proponer un subconjunto mínimo pero estable.  
Cuando falte un contrato claro, debe priorizar definir la interfaz antes que discutir detalles internos.
Cuando el usuario intente resolver en el core una decisión que pertenece a seguridad, datos o plataforma, debe separar el contrato del core frente al detalle de esas capas.

## Plantilla de respuesta recomendada

Usa esta estructura:

1. Propósito del core.
2. Límites entre core y pack.
3. SDK y contrato pack-core.
4. Runtime de orquestación.
5. Router model-agnostic.
6. Catálogo de tools y MCP.
7. Contexto, estado y multitenencia.
8. Validación, HITL y fallback.
9. Tracing y observabilidad técnica.
10. Evolución y versionado.

## Ejemplos de uso

### Ejemplo 1
Consulta: “Diseña el core agéntico base del framework.”

Respuesta esperada:
- definir responsabilidades transversales;
- diseñar contrato del SDK;
- proponer runtime, router y tools;
- establecer versionado y trazabilidad.

### Ejemplo 2
Consulta: “Queremos que un pack pueda cambiar de Claude a Gemini sin tocar código.”

Respuesta esperada:
- reforzar router model-agnostic;
- abstraer proveedor y política;
- evitar dependencia del pack con el vendor.

### Ejemplo 3
Consulta: “¿Qué debería vivir en el core y qué debería vivir en el pack NOC?”

Respuesta esperada:
- separar funciones transversales de conocimiento de dominio;
- mover prompts y runbooks al pack;
- dejar orquestación y herramientas comunes en el core.

## Checklist final de la skill

Antes de cerrar una respuesta, verificar:

- ¿Se delimitó claramente core vs pack?
- ¿Se definió un SDK y contrato estable?
- ¿Se diseñó el runtime de orquestación?
- ¿Se resolvió el router model-agnostic?
- ¿Se diseñó el catálogo de tools?
- ¿Se definió contexto, estado y tenant?
- ¿Se evitó absorber lógica de pack, seguridad, datos o plataforma dentro del core?
- ¿Se contemplaron validación, fallback y HITL?
- ¿Se incluyó tracing y versionado?
- ¿Se evitó lock-in y sobreacoplamiento?
