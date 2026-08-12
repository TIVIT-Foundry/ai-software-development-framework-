---
name: framework-scaffold-implementation
description: 'Usa esta skill para diseñar y aterrizar el scaffold e implementación
  inicial del framework. Sirve para definir estructura de repositorios, módulos, contratos
  del SDK, plantillas de packs, wiring del core, entorno local, pipelines y el primer
  vertical slice funcional. Trigger: Cuando la arquitectura está definida y se necesita
  convertir el diseño en repositorios, módulos, SDK y primer vertical slice.'
version: 1.0
metadata:
  when_to_use:
  - Cuando la arquitectura ya está definida y se necesita empezar a construir.
  - Cuando se quiere convertir el diseño del framework en una base ejecutable.
  - Cuando se necesita definir la estructura inicial de código y repositorios.
  - Cuando se quiere estandarizar cómo nace un nuevo pack o capacidad.
  - Cuando se necesita un MVP técnico del framework corriendo end-to-end.
  phase:
  - scaffold
  layer:
  - implementation
  enforcement: mandatory
  depends_on:
  - framework-core-design
  - framework-platform
  consumed_by:
  - framework-qa-validation
  - project-bootstrap
  agent_roles:
  - delivery-agent
  - design-agent
  validation_profile: skill-contract, documentation
  mcp_usage: optional
---

# framework-scaffold-implementation

## Propósito

Esta skill sirve para aterrizar el framework en una implementación inicial operable.  
Su función es convertir la arquitectura en una base de código, configuración y automatización que permita desarrollar nuevos packs y capacidades sobre un core común sin improvisación estructural.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Cómo se organiza el código del framework desde el inicio?
2. ¿Qué módulos, repos o paquetes deben existir primero?
3. ¿Cómo se materializa el SDK interno en código?
4. ¿Qué plantilla mínima necesita un nuevo pack?
5. ¿Qué componentes deben implementarse primero para validar el diseño?
6. ¿Cómo se levanta el framework localmente y en ambientes iniciales?
7. ¿Qué pipelines básicos hacen falta para entregar cambios con seguridad?
8. ¿Qué vertical slice demuestra que el framework funciona de punta a punta?

## Relación con otras skills

- `framework-architecture`, `framework-core-design`, `framework-data-memory-compliance`, `framework-security` y `framework-platform` entregan el diseño que esta skill convierte en código, estructura y automatización inicial.
- `framework-pack-design` define el pack de referencia que debe materializarse en el scaffold.
- `framework-qa-validation` consume esta skill para validar que el scaffold y el slice realmente cumplen contratos y criterios.

## Qué debe hacer el agente cuando esta skill está activa

El agente debe:

1. Proponer una estructura inicial simple pero escalable.
2. Traducir capas arquitectónicas a módulos y artefactos concretos.
3. Diseñar el scaffold del core, del SDK y de al menos un pack.
4. Definir contratos, interfaces y puntos de extensión.
5. Diseñar el bootstrap de entorno local y desarrollo.
6. Definir automatización básica de build, test, lint, deploy y observabilidad.
7. Priorizar un vertical slice que pruebe valor real.
8. Evitar sobre-ingeniería de day 1.
9. Mantener consistencia con seguridad, memoria y plataforma ya definidas.
10. Hacer evidente cómo agregar nuevos packs sin tocar la base innecesariamente.

## Entradas esperadas

Esta skill asume que ya existe:
- gobierno del framework;
- arquitectura general;
- diseño del core;
- diseño de datos y seguridad;
- lineamientos de plataforma.

Si estas bases no existen, la skill debe pedirlas antes de concluir.

## Alcance de la fase

La fase de scaffold e implementación sí incluye:
- estructura de repositorios;
- módulos iniciales;
- contratos base;
- paquetes compartidos;
- configuración inicial;
- plantillas de packs;
- wiring inicial;
- entorno local;
- docker compose o equivalente para desarrollo;
- pipelines básicos;
- primer vertical slice.

La fase de scaffold e implementación no incluye todavía:
- desarrollo completo de todos los packs;
- optimización avanzada de performance;
- endurecimiento total enterprise de cada componente;
- automatizaciones sofisticadas que no sean necesarias para arrancar.

## Principios que siempre debe respetar

- El scaffold debe reflejar la arquitectura, no contradecirla.
- El core debe nacer reusable, aunque el primer uso sea un solo pack.
- El pack debe depender del contrato del SDK, no de internals del core.
- El entorno local debe ser reproducible por cualquier desarrollador.
- El primer slice debe validar el framework, no solo compilar.
- Lo mínimo implementado debe ser real, no decorativo.
- La estructura debe facilitar crecimiento, no imponer reescritura temprana.
- El scaffold del MVP debe ser austero pero limpio.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- cómo aterrizar el diseño en repositorios, módulos y contratos iniciales;
- qué se implementa primero;
- cómo se levanta el entorno local;
- qué vertical slice valida la base del framework.

Esta skill delega:
- criterios de aceptación y estrategia de validación a `framework-qa-validation`;
- políticas de diseño a las skills previas de arquitectura, core, seguridad, datos y plataforma;
- operación continua y evolución a `framework-operations-evolution`.

## Qué debe definir el diseño

### 1. Estructura de repositorio
Definir:
- monorepo o multi-repo;
- módulos principales;
- librerías compartidas;
- paquetes del core;
- packs;
- infraestructura como código;
- configuración por entorno;
- convenciones de nombres.

### 2. Módulos iniciales
Definir como mínimo:
- interfaces de entrada;
- core runtime;
- sdk interno;
- router de modelos;
- catálogo o registry de tools;
- trazabilidad;
- memoria base;
- seguridad base;
- pack de ejemplo;
- utilidades compartidas.

### 3. Scaffold del SDK
Definir:
- interfaces públicas;
- clases base o abstracciones;
- contratos de agentes;
- contratos de tools;
- contratos de policies;
- objetos de contexto;
- versionado inicial;
- ejemplos de uso.

### 4. Scaffold del core
Definir:
- entrypoint de ejecución;
- runtime agéntico;
- registro de agentes;
- router;
- ejecución de tools;
- integración con tracing;
- hooks de validación;
- handling de errores;
- soporte de tenant y contexto.

### 5. Scaffold del pack
Definir:
- estructura de un pack nuevo;
- agentes;
- prompts o policies;
- tools propias;
- adapters;
- tests;
- archivo de manifest o metadata;
- puntos de extensión al core.

### 6. Entorno local y bootstrap
Definir:
- dependencias mínimas locales;
- docker compose o scripts de arranque;
- servicios emulados o reales;
- variables de entorno;
- datos seed;
- secretos de desarrollo;
- setup de observabilidad mínima.

### 7. Pipeline de implementación
Definir:
- lint;
- tests unitarios;
- pruebas de contrato;
- build de contenedores;
- escaneo básico;
- despliegue a ambiente dev;
- validación post-deploy.

### 8. Vertical slice inicial
Definir un caso mínimo de punta a punta que incluya:
- request entrante;
- resolución de tenant;
- ejecución de un agente;
- llamada a una tool;
- uso mínimo de memoria;
- trazabilidad;
- respuesta final;
- medición de costo o al menos telemetría base.

### 9. Extensibilidad
Definir:
- cómo se crea un nuevo pack;
- cómo se registra un nuevo agente;
- cómo se agrega una nueva tool;
- cómo se incorporan nuevas políticas;
- cómo evolucionan contratos sin romper implementaciones existentes.

### 10. Roadmap de implementación
Definir:
- qué entra en sprint 0;
- qué entra en sprint 1;
- qué valida el primer release interno;
- qué se posterga conscientemente.

## Preguntas guía

### 1. Sobre repos y módulos
- ¿Monorepo o multi-repo?
- ¿Qué paquetes deben versionarse juntos?
- ¿Qué módulos cambian con más frecuencia y cuáles deben ser más estables?

### 2. Sobre SDK
- ¿Qué interfaz mínima necesita un pack para correr?
- ¿Qué parte del SDK debe ser pública y estable?
- ¿Qué parte puede permanecer interna al core?

### 3. Sobre bootstrap
- ¿Qué necesita un desarrollador para correr el framework en su máquina?
- ¿Qué dependencias deben estar dockerizadas?
- ¿Qué configuraciones deben venir listas por defecto?

### 4. Sobre implementación inicial
- ¿Qué componentes deben existir de verdad desde el primer corte?
- ¿Qué puede mockearse temporalmente?
- ¿Qué componente no puede fingirse porque invalidaría el aprendizaje?

### 5. Sobre slice end-to-end
- ¿Qué caso demuestra mejor el valor del framework?
- ¿Qué slice prueba core, seguridad, memoria y trazabilidad a la vez?
- ¿Qué evidencia diría “esto ya es framework y no solo PoC”?

### 6. Sobre evolución
- ¿Cómo se agrega un segundo pack sin copiar y pegar?
- ¿Cómo se hacen cambios al core sin romper el primer pack?
- ¿Qué pruebas de contrato deben existir desde el día 1?

## Salidas esperadas de esta skill

Cuando esta skill responda, debe producir uno o varios de estos artefactos:

### A. Estructura inicial del repositorio
- módulo;
- responsabilidad;
- depende de;
- observaciones.

### B. Mapa de implementación por componente
- componente;
- prioridad;
- estado inicial;
- entregable;
- riesgo.

### C. Diseño del SDK en código
- interfaz;
- propósito;
- consumidor;
- estabilidad esperada.

### D. Plantilla de pack
- archivo o módulo;
- finalidad;
- obligatorio/opcional;
- extensión.

### E. Diseño del entorno local
- servicio;
- forma de arranque;
- dependencia;
- notas.

### F. Pipeline inicial
- etapa;
- herramienta;
- condición de éxito;
- salida.

### G. Vertical slice de referencia
- paso;
- componente involucrado;
- evidencia esperada.

### H. Roadmap de implementación
- fase;
- objetivo;
- entregable;
- criterio de done.

### I. Consumidores del scaffold
- consumidor;
- artefacto consumido;
- validación esperada;
- dependencia crítica.

## Criterios de calidad

La skill debe evaluar el diseño usando estos criterios:

- claridad de estructura;
- alineación con la arquitectura;
- facilidad de onboarding;
- reproducibilidad local;
- desacoplamiento pack-core;
- validación real mediante vertical slice;
- capacidad de evolucionar sin reescritura;
- austeridad suficiente para MVP.

## Comportamiento esperado del agente

Cuando la propuesta sea demasiado abstracta y no aterrice en módulos reales, el agente debe concretar.  
Cuando el scaffold copie la arquitectura en demasiados repos o proyectos sin necesidad, debe simplificar.  
Cuando el primer slice no pruebe el framework completo, debe endurecer el alcance.  
Cuando una decisión de implementación comprometa el contrato a largo plazo del SDK, debe marcar el riesgo.
Cuando una discusión cambie de implementación inicial a rediseño arquitectónico o a validación profunda, debe remitir esa parte a architecture o QA en lugar de mezclar fases.

## Plantilla de respuesta recomendada

Usa esta estructura:

1. Objetivo del scaffold.
2. Estructura inicial del código.
3. SDK y core base.
4. Plantilla de pack.
5. Entorno local y bootstrap.
6. Pipeline inicial.
7. Vertical slice de referencia.
8. Roadmap de implementación.
9. Riesgos y trade-offs.
10. Decisiones pendientes.

## Ejemplos de uso

### Ejemplo 1
Consulta: “Queremos arrancar con un solo pack pero dejar lista la base para varios.”

Respuesta esperada:
- monorepo o estructura compartida simple;
- core reusable;
- SDK mínimo;
- pack de ejemplo desacoplado.

### Ejemplo 2
Consulta: “¿Qué debemos tener implementado al final del sprint 0?”

Respuesta esperada:
- entorno local;
- runtime mínimo;
- tracing;
- pack demo;
- slice end-to-end;
- pipeline básico.

### Ejemplo 3
Consulta: “¿Cómo nace un nuevo pack dentro del framework?”

Respuesta esperada:
- plantilla estandarizada;
- manifest;
- agentes;
- tools;
- tests de contrato;
- registro en el core.

## Checklist final de la skill

Antes de cerrar una respuesta, verificar:

- ¿Se definió la estructura inicial del código?
- ¿Se diseñó el scaffold del SDK y del core?
- ¿Se diseñó la plantilla de pack?
- ¿Se resolvió el entorno local?
- ¿Se definió pipeline básico?
- ¿Se eligió un vertical slice real?
- ¿Se documentó cómo extender el framework?
- ¿Se indicó qué parte se valida en QA y qué parte evoluciona en operations?
- ¿Se evitó sobre-ingeniería para el MVP?
- ¿Se alineó todo con la arquitectura ya definida?
