---
name: framework-pack-design
description: 'Usa esta skill para diseñar un pack vertical como producto comercializable
  dentro del framework. Sirve para definir capacidades del pack, agentes especializados,
  prompts, runbooks, herramientas, integraciones nativas, configuración por tenant,
  métricas y límites del pack antes de implementarlo. Trigger: Cuando ya existe discovery
  y concepción funcional de un vertical y se necesita aterrizar el pack como producto
  comercializable.'
version: 1.0
metadata:
  when_to_use:
  - Cuando ya existe discovery y concepción funcional de un vertical.
  - Cuando se necesita aterrizar el pack como unidad de producto.
  - Cuando se quiere definir qué conocimiento de dominio pertenece al pack.
  - Cuando se requiere diseñar agentes especializados, prompts y runbooks del vertical.
  - Cuando se necesita separar lo reusable del pack frente a la personalización por
    tenant.
  phase:
  - conception
  layer:
  - design
  enforcement: mandatory
  depends_on:
  - framework-conception
  - framework-governance
  consumed_by:
  - framework-architecture
  - framework-qa-validation
  - framework-scaffold-implementation
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: skill-contract
  mcp_usage: optional
---

# framework-pack-design

## Propósito

Esta skill sirve para diseñar un pack vertical como producto reusable, modular y vendible dentro del framework.  
Su función es definir qué contiene el pack, cómo encapsula el conocimiento del dominio, qué agentes especializados ofrece, qué integraciones nativas requiere y cómo genera valor para distintos clientes sin romper el aislamiento por tenant.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Qué producto vertical estamos diseñando?
2. ¿Qué problema de dominio resuelve este pack?
3. ¿Qué capacidades funcionales forman parte del pack?
4. ¿Qué agentes especializados lo componen?
5. ¿Qué prompts, runbooks y reglas de dominio son parte de su propiedad intelectual?
6. ¿Qué herramientas e integraciones nativas necesita?
7. ¿Qué parte del pack es global y qué parte se configura por tenant?
8. ¿Cómo se mide el éxito del pack operativa y comercialmente?
9. ¿Cuál es el MVP real del pack?

## Relación con otras skills

- `framework-conception` define capacidades y flujos funcionales que esta skill convierte en producto vertical.
- `framework-architecture` y `framework-core-design` consumen esta skill para separar responsabilidades del pack frente al core.
- `framework-data-memory-compliance`, `framework-security` y `framework-platform` toman sus dependencias como requisitos de capa.
- `framework-scaffold-implementation` usa esta definición para crear la plantilla y el primer pack real.

## Qué debe hacer el agente cuando esta skill está activa

El agente debe:

1. Tomar como entrada el discovery y la concepción funcional del vertical.
2. Delimitar el pack como producto independiente.
3. Definir alcance, fronteras y propuesta de valor del pack.
4. Diseñar las capacidades especializadas del dominio.
5. Definir agentes, roles y responsabilidades dentro del pack.
6. Identificar prompts, runbooks, políticas y conocimiento curado que forman parte del activo propio.
7. Especificar herramientas e integraciones nativas del vertical.
8. Separar claramente:
   - conocimiento global del pack,
   - configuración por tenant,
   - datos propios del cliente.
9. Proponer métricas de adopción, calidad y valor del pack.
10. Delimitar un MVP del pack que sea comercializable y técnicamente viable.

## Entradas esperadas

Esta skill asume que ya existe:
- gobierno del framework;
- discovery vertical;
- concepción funcional;
- lineamientos arquitectónicos preliminares.

Si no existe esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase de diseño del pack vertical sí incluye:
- definición del pack como producto;
- propuesta de valor;
- límites funcionales;
- capacidades del pack;
- agentes especializados;
- prompts y runbooks;
- herramientas e integraciones del dominio;
- configuración por tenant;
- métricas del pack;
- MVP y releases futuros.

La fase de diseño del pack vertical no incluye todavía:
- diseño completo del core;
- implementación técnica final;
- infraestructura detallada;
- políticas de seguridad completas fuera de lo que afecte el comportamiento del pack.

## Principios que siempre debe respetar

- El pack es modular e independiente de otros packs.
- El pack comparte core, modelos, memoria, control e infraestructura con el framework.
- El pack encapsula conocimiento experto del dominio.
- Los prompts, runbooks y métricas del pack son parte del Build diferenciador.
- Los activos del pack deben poder versionarse sin contaminar datos del cliente ni romper configuraciones por tenant.
- El conocimiento curado del pack puede ser global.
- Los datos consumidos del cliente deben estar estrictamente aislados por tenant.
- El pack debe poder venderse, activarse y evolucionar por separado.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- la identidad del pack como producto;
- sus capacidades y límites de negocio;
- sus agentes especializados, prompts y runbooks;
- sus integraciones nativas y métricas;
- qué es activo global del pack y qué es configuración por tenant.

Esta skill delega:
- contratos y runtime comunes a `framework-core-design`;
- estructura técnica a `framework-architecture`;
- controles, stores e infraestructura a `framework-security`, `framework-data-memory-compliance` y `framework-platform`.

## Qué debe definir el diseño del pack

### 1. Identidad del pack
Definir:
- nombre del pack;
- dominio o vertical;
- problema principal que resuelve;
- usuarios o áreas objetivo;
- propuesta de valor;
- diferenciadores.

### 2. Alcance del pack
Definir:
- qué casos de uso cubre;
- qué casos de uso no cubre;
- fronteras con otros packs;
- alcance del MVP;
- extensiones futuras.

### 3. Capacidades del pack
Definir:
- capacidades principales;
- capacidades secundarias;
- dependencias entre capacidades;
- prioridad para MVP y roadmap.

### 4. Agentes especializados
Definir:
- nombre del agente;
- rol dentro del vertical;
- entradas;
- decisiones;
- herramientas que usa;
- salidas;
- nivel de autonomía;
- necesidad de human-in-the-loop.

### 5. Prompts y runbooks
Definir:
- qué prompts base necesita cada agente;
- qué runbooks operativos o de decisión usa;
- qué políticas o reglas de dominio deben incorporarse;
- qué partes son estáticas y cuáles parametrizables;
- qué conocimiento debe versionarse como activo del pack.

### 6. Herramientas e integraciones nativas
Definir:
- sistemas externos del dominio;
- acciones obligatorias;
- herramientas del pack;
- conectores prioritarios;
- integraciones del MVP vs posteriores.

### 7. Configuración por tenant
Definir:
- parámetros configurables;
- políticas específicas por cliente;
- límites de autonomía;
- fuentes de datos activadas;
- herramientas habilitadas;
- presupuesto o SLA del tenant si aplica.

### 8. Dependencias con el framework
Definir:
- qué necesita del core agéntico;
- qué necesita de modelos;
- qué memoria requiere;
- qué controles de seguridad y trazabilidad exige;
- qué requisitos de infraestructura lo condicionan.

### 9. Métricas del pack
Definir:
- métricas operativas;
- métricas de calidad;
- métricas de adopción;
- métricas de negocio;
- métricas comercializables para el cliente.

### 10. Gestión de activos del pack
Definir:
- qué prompts, runbooks, playbooks, plantillas o reglas son activos versionados del pack;
- qué responsable aprueba cambios a esos activos;
- cómo se separa una nueva versión del activo frente a una personalización por tenant;
- qué cambios requieren coordinación con core, seguridad o QA;
- cómo se retiran o reemplazan activos obsoletos.

## Preguntas guía

### 1. Sobre el producto
- ¿Qué hace único a este pack?
- ¿Qué problema del vertical resuelve mejor que una solución genérica?
- ¿Qué lo hace vendible como unidad separada?

### 2. Sobre el alcance
- ¿Qué entra realmente al pack?
- ¿Qué parte pertenece al core y no al pack?
- ¿Qué parte pertenece a personalización del cliente y no al pack base?

### 3. Sobre los agentes
- ¿Cuántos agentes especializados necesita el pack?
- ¿Qué responsabilidad clara tiene cada uno?
- ¿Cuál coordina y cuál ejecuta tareas concretas?

### 4. Sobre conocimiento del dominio
- ¿Qué runbooks del vertical deben codificarse?
- ¿Qué reglas, heurísticas o criterios expertos deben quedar incorporados?
- ¿Qué partes pueden cambiar por industria o por tenant?

### 5. Sobre herramientas
- ¿Qué tools necesita sí o sí el pack para ser útil?
- ¿Qué integraciones son nativas del vertical?
- ¿Qué herramientas se pueden mockear en MVP?

### 6. Sobre multi-tenancy
- ¿Qué conocimiento del pack es global?
- ¿Qué configuración cambia por tenant?
- ¿Qué datos del cliente nunca deben formar parte del conocimiento global?

### 7. Sobre valor
- ¿Cómo sabremos que el pack está funcionando bien?
- ¿Qué KPI puede comprar o entender un cliente?
- ¿Qué evidencia de ROI o productividad puede mostrar el pack?

## Salidas esperadas de esta skill

Cuando esta skill responda, debe producir uno o varios de estos artefactos:

### A. Ficha del pack
- nombre;
- vertical;
- propósito;
- propuesta de valor;
- usuarios objetivo;
- diferenciadores.

### B. Mapa de capacidades del pack
- capacidad;
- descripción;
- prioridad;
- dependencia;
- entra/no entra al MVP.

### C. Catálogo de agentes especializados
- agente;
- responsabilidad;
- entradas;
- decisiones;
- herramientas;
- salidas;
- HITL.

### D. Inventario de prompts y runbooks
- agente;
- prompt base;
- runbook asociado;
- tipo de conocimiento;
- versionado;
- parametrización por tenant.

### E. Mapa de herramientas e integraciones
- sistema;
- acción;
- criticidad;
- disponibilidad en MVP;
- observaciones.

### F. Configuración por tenant
- parámetro;
- descripción;
- obligatorio/opcional;
- impacto operativo.

### G. Dependencias con el framework
- dependencia;
- capa afectada;
- justificación;
- riesgo si falta.

### H. Métricas del pack
- métrica;
- tipo;
- objetivo;
- interpretación.

### I. Definición de MVP del pack
- qué entra;
- qué se excluye;
- supuestos;
- riesgos;
- siguiente release.

### J. Catálogo de activos del pack
- activo;
- tipo;
- versión;
- propietario;
- parametrizable por tenant sí/no;
- dependencia con otras capas.

### K. Consumidores del diseño del pack
- consumidor;
- artefacto consumido;
- uso esperado;
- riesgo si falta.

## Criterios de calidad del pack

La skill debe evaluar el diseño del pack usando estos criterios:

- claridad de propuesta de valor;
- especificidad del conocimiento de dominio;
- separación correcta entre pack, core y tenant;
- modularidad;
- independencia frente a otros packs;
- utilidad real del MVP;
- facilidad de activación por cliente;
- capacidad de evolución comercial;
- medibilidad del valor generado.

## Comportamiento esperado del agente

Cuando el pack esté demasiado genérico, el agente debe forzarlo a especializarse.  
Cuando el usuario mezcle cosas del core con cosas del pack, el agente debe separarlas explícitamente.  
Cuando una integración sea deseable pero no crítica, debe clasificarla como posterior.  
Cuando detecte que el pack depende demasiado de personalización ad hoc por cliente, debe advertir que el producto aún no está suficientemente empaquetado.
Cuando un prompt o runbook del pack dependa de datos del cliente para existir, debe marcar riesgo de contaminación entre activo global y configuración por tenant.
Cuando una pregunta pase de producto a contrato técnico o enforcement operativo, debe mantener la decisión del pack y remitir la implementación de esa capa a architecture, core, security, data o platform.

## Plantilla de respuesta recomendada

Usa esta estructura:

1. Identidad y propósito del pack.
2. Propuesta de valor.
3. Alcance y límites.
4. Capacidades del pack.
5. Agentes especializados.
6. Prompts, runbooks y conocimiento curado.
7. Herramientas e integraciones nativas.
8. Configuración por tenant.
9. Métricas del pack.
10. MVP y evolución esperada.

## Ejemplos de uso

### Ejemplo 1
Consulta: “Diseña el pack vertical de NOC.”

Respuesta esperada:
- definir triage, diagnóstico inicial, runbooks y escalamiento;
- especificar agentes del dominio;
- separar conocimiento global del pack frente a datos del cliente;
- definir KPI como tiempo de clasificación o reducción de carga L1.

### Ejemplo 2
Consulta: “Queremos aterrizar el pack de Cloud FinOps.”

Respuesta esperada:
- definir análisis de costos, drift, rightsizing y compliance;
- proponer tools e integraciones cloud;
- establecer configuraciones por tenant y métricas comercializables.

### Ejemplo 3
Consulta: “Nuestro pack de Customer Engagement se está volviendo demasiado amplio.”

Respuesta esperada:
- recortar capacidades;
- separar MVP de roadmap;
- definir subdominios o subpacks si es necesario.

## Checklist final de la skill

Antes de cerrar una respuesta, verificar:

- ¿Se definió el pack como producto?
- ¿Se delimitó su alcance?
- ¿Se identificaron agentes especializados?
- ¿Se definieron prompts y runbooks?
- ¿Se listaron tools e integraciones nativas?
- ¿Se separó correctamente lo global del pack frente a lo configurable por tenant?
- ¿Se identificaron y versionaron los activos propios del pack?
- ¿Se definieron métricas claras?
- ¿Se indicó qué dependencias continúan en architecture, core, data, security y platform?
- ¿Se delimitó un MVP comercializable?
