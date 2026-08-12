---
name: framework-discovery
description: 'Usa esta skill para descubrir y delimitar un vertical de negocio antes
  de diseñar el pack, los agentes o la arquitectura detallada. Sirve para entender
  problema, actores, procesos, datos, integraciones, restricciones y métricas del
  dominio. Trigger: Cuando se quiere iniciar el análisis de un nuevo vertical, validar
  si un dominio justifica un pack propio, o se necesita entender procesos y actores
  del negocio.'
version: 1.0
metadata:
  when_to_use:
  - Cuando se quiere iniciar el análisis de un nuevo vertical.
  - Cuando se necesita validar si un dominio justifica un pack propio.
  - Cuando se requiere entender procesos, actores y datos antes de diseñar agentes.
  - Cuando se debe priorizar un caso de uso inicial dentro de un vertical.
  - Cuando se desea preparar insumos para conception, pack design y architecture.
  phase:
  - inception
  layer:
  - business
  enforcement: mandatory
  depends_on:
  - framework-governance
  consumed_by:
  - framework-conception
  agent_roles:
  - design-agent
  - orchestrator-agent
  validation_profile: documentation
  mcp_usage: optional
---

# framework-discovery

## Propósito

Esta skill sirve para entender el dominio de negocio antes de diseñar la solución.  
Su función es identificar el problema real, los usuarios, los procesos, las integraciones, la información disponible y los indicadores de valor, de modo que el vertical quede bien delimitado y pueda convertirse en un pack comercializable.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Qué vertical o dominio estamos atendiendo?
2. ¿Qué problema concreto vale la pena resolver primero?
3. ¿Qué actores intervienen y cómo trabajan hoy?
4. ¿Qué tareas, decisiones o flujos son candidatos para asistencia o automatización con agentes?
5. ¿Qué datos, documentos, runbooks y sistemas necesita el futuro pack?
6. ¿Qué métricas demostrarían valor de negocio y valor operativo?
7. ¿Qué restricciones regulatorias, técnicas o de seguridad condicionan la solución?

## Relación con otras skills

- `framework-governance` define principios y restricciones que discovery debe recoger como contexto del vertical.
- `framework-discovery` entrega insumos a `framework-conception`, `framework-pack-design` y `framework-architecture`.
- Esta skill no diseña la solución técnica; prepara el terreno para las skills de concepción y diseño.

## Definición de vertical

Un vertical es un dominio de negocio específico para el cual se construye una solución especializada.  
El vertical encapsula conocimiento experto, lenguaje de dominio, procesos recurrentes, integraciones propias, reglas operativas y criterios de éxito particulares.

Ejemplos de vertical:
- NOC / MSP
- SOC
- Cloud / FinOps
- Telco
- Customer Engagement
- HR
- Financial Ops
- Procurement
- Document Intelligence
- Field Service

## Qué debe hacer el agente cuando esta skill está activa

El agente debe:

1. Delimitar claramente el vertical analizado.
2. Identificar problema principal, subproblemas y alcance inicial.
3. Levantar actores, responsabilidades y puntos de dolor.
4. Describir procesos actuales y dónde hay fricción.
5. Detectar decisiones repetitivas, manuales o lentas que puedan asistir agentes.
6. Inventariar sistemas, fuentes de datos, documentos y eventos relevantes.
7. Identificar restricciones regulatorias, de privacidad, compliance o sensibilidad del dato.
8. Priorizar casos de uso por valor de negocio y factibilidad.
9. Preparar insumos para el diseño del pack vertical.
10. No diseñar aún la arquitectura detallada del core, salvo identificar dependencias evidentes.

## Alcance de la fase

La fase de discovery vertical sí incluye:
- comprensión del negocio;
- comprensión del proceso;
- actores y roles;
- datos e integraciones;
- puntos de dolor;
- oportunidades de automatización o asistencia;
- criterios de éxito;
- riesgos y vacíos de información.

La fase de discovery vertical no incluye todavía:
- diseño técnico detallado del core;
- selección final de tecnologías;
- definición completa de prompts;
- implementación;
- decisiones cerradas de infraestructura.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- cómo delimitar el vertical;
- qué problema priorizar primero;
- qué actores, procesos, datos y restricciones son relevantes;
- qué caso inicial parece más valioso o viable.

Esta skill delega:
- la solución funcional a `framework-conception`;
- la forma de producto a `framework-pack-design`;
- la estructura técnica a `framework-architecture`.

## Preguntas guía

### 1. Sobre el negocio
- ¿Cuál es el dominio o vertical?
- ¿Qué problema estratégico o operativo se busca resolver?
- ¿Por qué este problema importa ahora?
- ¿Cómo se mide hoy el impacto del problema?

### 2. Sobre los usuarios
- ¿Quién usa o se beneficia de la solución?
- ¿Quién opera el proceso hoy?
- ¿Quién toma decisiones críticas?
- ¿Quién aprueba, escala o cierra casos?

### 3. Sobre los procesos
- ¿Cuál es el flujo actual de trabajo?
- ¿Qué pasos son manuales, repetitivos o lentos?
- ¿Dónde hay errores, retrabajo o dependencia de expertos?
- ¿Qué decisiones siguen reglas conocidas y cuáles requieren juicio humano?

### 4. Sobre datos y conocimiento
- ¿Qué documentos, tickets, bases, catálogos o runbooks existen?
- ¿Qué información está estructurada y cuál no?
- ¿Qué tan confiables son los datos?
- ¿Qué conocimiento vive en personas y no en sistemas?

### 5. Sobre sistemas e integraciones
- ¿Qué sistemas participan hoy?
- ¿Qué eventos de entrada disparan el proceso?
- ¿Qué acciones o salidas debería producir el agente?
- ¿Qué integraciones serán obligatorias en un MVP?

### 6. Sobre riesgo y compliance
- ¿Hay datos sensibles, PII, PHI o secretos?
- ¿Hay requisitos regulatorios o sectoriales?
- ¿Qué decisiones no pueden automatizarse sin revisión humana?
- ¿Qué errores serían inaceptables?

### 7. Sobre valor
- ¿Qué KPI mejoraría la solución?
- ¿Qué ahorro, velocidad o calidad se espera?
- ¿Qué caso de uso sería el primer slice más rentable o viable?

## Salidas esperadas de esta skill

Cuando esta skill responda, debe producir uno o varios de estos artefactos:

### A. Perfil del vertical
- nombre del vertical;
- contexto del dominio;
- problema principal;
- oportunidad de negocio;
- actores clave.

### B. Mapa del proceso actual
- pasos del proceso;
- entradas;
- decisiones;
- salidas;
- fricciones.

### C. Inventario de conocimiento y datos
- documentos;
- runbooks;
- fuentes estructuradas;
- fuentes no estructuradas;
- sistemas fuente;
- calidad del dato.

### D. Backlog inicial de casos de uso
- caso de uso;
- usuario beneficiado;
- valor esperado;
- complejidad;
- prioridad.

### E. Riesgos y restricciones
- regulatorios;
- operativos;
- de seguridad;
- de datos;
- de adopción.

### F. Recomendación de foco inicial
- primer caso de uso recomendado;
- alcance de MVP del vertical;
- exclusiones iniciales.

### G. Consumidores del discovery
- consumidor;
- artefacto consumido;
- decisión habilitada;
- vacío pendiente.

## Criterios de priorización

La skill debe priorizar casos de uso usando estos criterios:

- valor de negocio;
- frecuencia del problema;
- costo actual del proceso;
- calidad y disponibilidad de datos;
- facilidad de integración;
- riesgo operativo;
- riesgo regulatorio;
- tiempo estimado para un MVP;
- posibilidad de demostrar impacto rápido.

## Comportamiento esperado del agente

Cuando el usuario describa un dominio de forma ambigua, el agente debe ayudar a acotarlo.  
Cuando existan muchos casos posibles, debe priorizar en lugar de listar todo sin criterio.  
Cuando falte información crítica, debe pedirla antes de concluir.  
Cuando detecte que el dominio no justifica un pack propio, debe decirlo explícitamente.
Cuando la conversación derive hacia solución funcional o arquitectura, debe cerrar discovery con supuestos claros y remitir la siguiente decisión a la skill adecuada.

## Plantilla de respuesta recomendada

Usa esta estructura:

1. Definición del vertical.
2. Problema principal y contexto.
3. Actores involucrados.
4. Proceso actual y fricciones.
5. Datos, sistemas e integraciones.
6. Riesgos y restricciones.
7. Casos de uso candidatos.
8. Recomendación del primer caso de uso.
9. Vacíos de información pendientes.

## Ejemplos de uso

### Ejemplo 1
Consulta: “Queremos explorar un pack para NOC.”

Respuesta esperada:
- delimitar qué tipo de NOC;
- identificar tipos de tickets, herramientas, runbooks y escalamiento;
- detectar tareas L1/L2 repetitivas;
- proponer un primer caso de uso como triage o diagnóstico inicial.

### Ejemplo 2
Consulta: “¿Tiene sentido un vertical de Customer Engagement?”

Respuesta esperada:
- identificar journeys, canales, intenciones frecuentes y handoff;
- separar atención transaccional de atención consultiva;
- recomendar si conviene un pack único o subpacks.

### Ejemplo 3
Consulta: “Tenemos datos dispersos de FinOps, ¿vale la pena?”

Respuesta esperada:
- evaluar calidad de datos, fuentes y decisiones actuales;
- identificar si el mayor valor está en análisis, alertas o recomendaciones;
- definir el slice inicial más viable.

## Checklist final de la skill

Antes de cerrar una respuesta, verificar:

- ¿Se delimitó claramente el vertical?
- ¿Se definió el problema principal?
- ¿Se identificaron actores y proceso actual?
- ¿Se levantaron datos, runbooks y sistemas?
- ¿Se detectaron restricciones y riesgos?
- ¿Se priorizaron casos de uso con criterio?
- ¿Se recomendó un foco inicial?
- ¿Se indicó qué parte continúa en conception, pack-design o architecture?
- ¿Se dejaron claros los vacíos pendientes?
