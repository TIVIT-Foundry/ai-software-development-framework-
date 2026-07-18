---
name: framework-conception
description: 'Usa esta skill para transformar el discovery de un vertical en una solución
  funcional concreta. Sirve para definir capacidades, agentes, flujos, herramientas,
  reglas, puntos de intervención humana, alcance de MVP y criterios de aceptación
  antes del diseño técnico detallado. Trigger: Cuando ya existe un discovery vertical
  y se necesita convertirlo en solución funcional, definiendo capacidades, agentes,
  flujos y alcance de MVP.'
version: 1.0
metadata:
  when_to_use:
  - Cuando ya existe un discovery vertical y se necesita convertirlo en solución funcional.
  - Cuando se requiere definir qué hará exactamente el pack.
  - Cuando se desea pasar de problemas detectados a capacidades, casos de uso y backlog.
  - Cuando se necesita delimitar MVP, exclusiones y criterios de aceptación.
  - Cuando se quiere preparar insumos para arquitectura, seguridad, QA e implementación.
  phase:
  - conception
  layer:
  - business
  enforcement: mandatory
  depends_on:
  - framework-discovery
  consumed_by:
  - framework-architecture
  - framework-pack-design
  agent_roles:
  - design-agent
  - orchestrator-agent
  validation_profile: documentation, skill-contract
  mcp_usage: optional
---

# framework-conception

## Propósito

Esta skill sirve para convertir el entendimiento del dominio en una definición funcional clara del producto.  
Su función es diseñar qué capacidades tendrá el pack, cómo se organizarán los agentes, qué flujos cubrirán, qué entradas procesarán, qué acciones producirán y qué valor funcional entregarán.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Qué solución funcional vamos a construir para este vertical?
2. ¿Qué capacidades principales tendrá el pack?
3. ¿Qué agentes o roles funcionales existirán?
4. ¿Qué casos de uso entran al MVP y cuáles quedan fuera?
5. ¿Qué flujos requieren automatización, asistencia o validación humana?
6. ¿Qué herramientas, acciones y salidas necesita cada flujo?
7. ¿Qué reglas de negocio y criterios de aceptación deben cumplirse?

## Relación con otras skills

- `framework-discovery` aporta el problema, actores, datos y restricciones que esta skill convierte en solución funcional.
- `framework-pack-design` toma esta definición para convertirla en producto vertical y activos del pack.
- `framework-architecture` consume esta skill para traducir capacidades y flujos a componentes y contratos técnicos.
- `framework-qa-validation` reutiliza criterios de aceptación definidos aquí.

## Qué debe hacer el agente cuando esta skill está activa

El agente debe:

1. Tomar como entrada el discovery del vertical.
2. Traducir problemas y oportunidades en capacidades funcionales.
3. Definir casos de uso concretos y priorizados.
4. Identificar agentes, subagentes o roles funcionales necesarios.
5. Diseñar flujos de interacción, decisión, ejecución y handoff.
6. Precisar entradas, salidas y acciones esperadas por flujo.
7. Definir cuándo hay automatización total, recomendación asistida o human-in-the-loop.
8. Delimitar claramente el MVP.
9. Convertir la solución en backlog funcional y criterios de aceptación.
10. No cerrar aún decisiones técnicas profundas de infraestructura o proveedor, salvo dependencias funcionales evidentes.

## Entradas esperadas

Esta skill asume que ya existe información de discovery, como:
- vertical definido;
- problema principal;
- actores;
- procesos actuales;
- datos y sistemas relevantes;
- restricciones del dominio;
- oportunidades priorizadas.

Si esa información no existe, la skill debe pedirla antes de continuar.

## Alcance de la fase

La fase de concepción funcional sí incluye:
- definición de capacidades del pack;
- catálogo funcional de agentes;
- casos de uso;
- flujos funcionales;
- entradas y salidas;
- acciones e integraciones necesarias;
- reglas de negocio;
- criterios de aceptación;
- recorte de MVP.

La fase de concepción funcional no incluye todavía:
- selección final de proveedores;
- diseño detallado del core;
- definición de infraestructura;
- implementación;
- configuración concreta de modelos;
- políticas técnicas finales de seguridad.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- qué solución funcional se construye;
- qué capacidades y casos de uso entran;
- qué agentes o roles funcionales participan;
- qué flujos, reglas y criterios de aceptación definen el MVP.

Esta skill delega:
- la forma de producto y activos del vertical a `framework-pack-design`;
- la arquitectura técnica a `framework-architecture`;
- la implementación a `framework-scaffold-implementation`.

## Preguntas guía

### 1. Sobre la solución
- ¿Qué debe hacer el pack para resolver el problema principal?
- ¿Qué resultado funcional espera el usuario o el cliente?
- ¿Cuál es el alcance inicial razonable del producto?

### 2. Sobre capacidades
- ¿Qué capacidades principales componen la solución?
- ¿Cuáles son imprescindibles para el MVP?
- ¿Cuáles pueden dejarse para una fase posterior?

### 3. Sobre agentes
- ¿Qué agentes o roles funcionales necesita el pack?
- ¿Qué responsabilidad tiene cada uno?
- ¿Cuál coordina, cuál analiza, cuál ejecuta y cuál valida?

### 4. Sobre flujos
- ¿Cuál es el flujo funcional de cada caso de uso?
- ¿Qué evento o input inicia el flujo?
- ¿Qué decisiones se toman durante el proceso?
- ¿Qué acciones ejecuta el sistema?
- ¿Qué salida entrega al usuario o sistema externo?
- ¿Dónde se necesita aprobación o supervisión humana?

### 5. Sobre herramientas e integraciones
- ¿Qué herramientas necesita invocar el agente?
- ¿Qué sistemas externos son funcionalmente obligatorios?
- ¿Qué acciones debe poder ejecutar el pack?
- ¿Qué integraciones pueden simularse en el MVP?

### 6. Sobre reglas de negocio
- ¿Qué condiciones deben cumplirse antes de actuar?
- ¿Qué validaciones son obligatorias?
- ¿Qué restricciones o límites aplican?
- ¿Qué comportamiento sería inaceptable?

### 7. Sobre priorización
- ¿Qué caso de uso entrega más valor con menor complejidad?
- ¿Qué capacidades forman el vertical mínimo viable?
- ¿Qué se excluye explícitamente del MVP?

## Salidas esperadas de esta skill

Cuando esta skill responda, debe producir uno o varios de estos artefactos:

### A. Definición funcional del pack
- nombre del pack;
- propósito;
- problema que resuelve;
- usuarios objetivo;
- alcance funcional.

### B. Mapa de capacidades
- capacidad;
- descripción;
- prioridad;
- dependencia;
- entra/no entra al MVP.

### C. Catálogo funcional de agentes
- nombre del agente;
- responsabilidad;
- entradas;
- decisiones;
- acciones;
- salidas;
- necesidad de HITL.

### D. Casos de uso priorizados
- caso de uso;
- actor principal;
- valor esperado;
- complejidad;
- prioridad;
- estado en MVP.

### E. Flujos funcionales
- disparador;
- secuencia de pasos;
- decisiones;
- excepciones;
- intervención humana;
- resultado esperado.

### F. Reglas de negocio
- regla;
- contexto;
- validación;
- impacto si falla.

### G. Criterios de aceptación
- condiciones de éxito por caso de uso;
- errores esperados;
- salidas mínimas aceptables;
- observaciones de negocio.

### H. Definición de MVP
- qué entra;
- qué no entra;
- supuestos;
- riesgos;
- siguientes fases.

### I. Consumidores de la concepción funcional
- consumidor;
- artefacto consumido;
- decisión habilitada;
- riesgo si falta.

## Criterios de priorización

La skill debe priorizar usando criterios como:

- valor de negocio;
- frecuencia de uso;
- urgencia operativa;
- riesgo de error humano actual;
- dependencia de expertos;
- disponibilidad de datos;
- complejidad funcional;
- factibilidad de integraciones;
- tiempo estimado para demostrar valor.

## Comportamiento esperado del agente

Cuando existan muchos casos de uso, el agente debe estructurarlos en MVP, siguiente release y backlog futuro.  
Cuando un flujo sea demasiado amplio, debe dividirlo en slices funcionales.  
Cuando detecte que algo aún no está suficientemente entendido, debe devolverlo como supuesto o vacío pendiente.  
Cuando una funcionalidad contradiga gobierno del framework, debe escalarlo como observación y no asumirlo como válido.
Cuando la discusión pase de capacidades a contratos técnicos o diseño del runtime, debe cerrar la decisión funcional y remitir el detalle a architecture o pack-design según corresponda.

## Plantilla de respuesta recomendada

Usa esta estructura:

1. Objetivo funcional del pack.
2. Capacidades principales.
3. Casos de uso priorizados.
4. Catálogo de agentes o roles funcionales.
5. Flujos clave.
6. Herramientas e integraciones necesarias.
7. Reglas de negocio.
8. Criterios de aceptación.
9. Definición de MVP.
10. Riesgos y vacíos pendientes.

## Ejemplos de uso

### Ejemplo 1
Consulta: “Ya hicimos discovery de NOC. Ahora define la solución funcional.”

Respuesta esperada:
- definir capacidades como triage, diagnóstico inicial, recomendación de runbook y escalamiento;
- separar qué hace el agente y qué requiere operador;
- proponer un MVP funcional con uno o dos flujos bien cerrados.

### Ejemplo 2
Consulta: “Queremos aterrizar el pack de Customer Engagement.”

Respuesta esperada:
- separar capacidades transaccionales, knowledge, sentiment y handoff;
- definir agentes funcionales;
- establecer qué journeys entran primero al MVP.

### Ejemplo 3
Consulta: “Tenemos varios problemas detectados en FinOps, ordénalos.”

Respuesta esperada:
- convertir hallazgos en capacidades funcionales;
- priorizar alertas, recomendaciones o análisis;
- proponer un backlog con alcance incremental.

## Checklist final de la skill

Antes de cerrar una respuesta, verificar:

- ¿Se transformó el discovery en capacidades funcionales?
- ¿Se definieron casos de uso concretos?
- ¿Se identificaron agentes o roles funcionales?
- ¿Se diseñaron flujos claros?
- ¿Se definieron entradas, acciones y salidas?
- ¿Se establecieron reglas de negocio?
- ¿Se definieron criterios de aceptación?
- ¿Se delimitó el MVP?
- ¿Se indicó qué parte continúa en pack-design, architecture y QA?
- ¿Se documentaron exclusiones y vacíos pendientes?
