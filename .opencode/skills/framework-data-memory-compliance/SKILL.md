---
name: framework-data-memory-compliance
description: 'Usa esta skill para diseñar la capa de datos, memoria y cumplimiento
  del framework. Sirve para definir taxonomía de datos, tipos de memoria, stores,
  aislamiento por tenant, retención, borrado, cifrado, clasificación de sensibilidad,
  controles de acceso y obligaciones de compliance. Trigger: Cuando se necesita diseñar
  la capa de datos, memoria y cumplimiento: taxonomía, stores, retención, cifrado
  y controles.'
version: 1.1
metadata:
  when_to_use:
  - Cuando se necesita diseñar la capa 5 del framework y su relación con compliance.
  - Cuando se quiere definir qué memoria necesita un pack o el core.
  - Cuando se debe separar datos globales, datos por tenant y datos efímeros.
  - Cuando se requiere establecer retención, borrado, cifrado y clasificación de datos.
  - Cuando se necesita preparar la solución para sectores regulados o clientes enterprise.
  phase:
  - architecture
  layer:
  - design
  enforcement: mandatory
  depends_on:
  - framework-architecture
  consumed_by:
  - costos-llm
  - framework-platform
  - framework-scaffold-implementation
  - framework-core-design
  agent_roles:
  - control-agent
  - design-agent
  validation_profile: tenant-isolation, security-review
  mcp_usage: none
---

# framework-data-memory-compliance

## Propósito

Esta skill sirve para diseñar cómo el framework maneja información, contexto y cumplimiento normativo.  
Su función es definir qué datos existen, qué memorias usa el sistema, cómo se almacenan, cómo se aíslan por tenant, cómo se protegen y cómo se gobiernan durante todo su ciclo de vida.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Qué tipos de datos maneja la solución?
2. ¿Qué tipos de memoria necesita el agente y con qué finalidad?
3. ¿Qué store o fuente de verdad corresponde a cada tipo de dato?
4. ¿Qué información es efímera, persistente, global o específica por tenant?
5. ¿Cómo se garantiza aislamiento físico y lógico entre tenants?
6. ¿Qué datos son sensibles y qué controles requieren?
7. ¿Qué políticas de retención, borrado, cifrado y auditoría aplican?
8. ¿Qué obligaciones regulatorias o de compliance impactan el diseño?

## Relación con otras skills

- `framework-architecture` define el papel de datos y memoria en la solución y los contratos que esta skill debe aterrizar.
- `framework-core-design` consume esta skill para saber qué memorias existen, qué contexto puede usar y qué límites de persistencia respetar.
- `framework-security` complementa esta skill con controles de acceso, auditoría y protección sobre los datos definidos aquí.
- `framework-platform` soporta los stores, el cifrado operativo, la residencia y la observabilidad de la capa de datos.
- `framework-operations-evolution` usa estas políticas para operar retención, borrado, evidencias y auditorías.

## Qué debe hacer el agente cuando esta skill está activa

El agente debe:

1. Identificar y clasificar los tipos de datos que intervienen en la solución.
2. Diseñar la estrategia de memoria del sistema.
3. Asignar cada tipo de información al store más adecuado.
4. Separar claramente:
   - conocimiento global del pack,
   - configuración del tenant,
   - datos del cliente,
   - estado efímero de sesión.
5. Diseñar aislamiento por tenant en datos, índices, grafos, claves y operación.
6. Definir sensibilidad de datos y controles asociados.
7. Diseñar políticas de retención, borrado y derecho al olvido.
8. Incorporar compliance desde el diseño, no como post-proceso.
9. Asegurar trazabilidad del uso, acceso y eliminación de información.
10. Evitar que memoria útil se convierta en riesgo regulatorio o contaminación entre clientes.

## Entradas esperadas

Esta skill asume que ya existe:
- gobierno del framework;
- arquitectura general;
- diseño preliminar del core y/o packs;
- identificación básica de casos de uso y datos relevantes.

Si falta esa base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase de datos, memoria y compliance sí incluye:
- clasificación de datos;
- diseño de memorias;
- stores y fuentes de verdad;
- aislamiento multi-tenant;
- cifrado;
- políticas de acceso;
- retención;
- borrado;
- auditoría;
- cumplimiento regulatorio;
- trazabilidad del uso de datos.

La fase de datos, memoria y compliance no incluye todavía:
- implementación detallada de pipelines de datos;
- operación legal completa fuera del sistema;
- certificaciones formales ya obtenidas;
- gobierno corporativo documental más amplio que exceda el framework.

## Principios que siempre debe respetar

- Sin aislamiento entre tenants no hay memoria válida en el framework.
- El conocimiento global del pack no debe contaminarse con datos del cliente.
- Cada tipo de memoria debe tener finalidad explícita.
- No todo dato debe convertirse en memoria.
- La memoria debe ser útil, trazable y gobernable.
- El borrado debe ser real, verificable y auditable.
- Los datos sensibles requieren controles proporcionales a su riesgo.
- Compliance debe verse como feature de producto y requisito contractual.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- la taxonomía de datos;
- los tipos de memoria y su finalidad;
- el store o source of truth de cada dato;
- el aislamiento por tenant en datos y memoria;
- la política de sensibilidad, retención, borrado y residencia.

Esta skill delega:
- enforcement de acceso, secretos y guardrails a `framework-security`;
- topología operativa, backups y despliegue de stores a `framework-platform`;
- uso del contexto y contrato de ejecución a `framework-core-design`.

## Taxonomía base de memoria

### 1. Memoria de sesión
Definir:
- contexto activo de una conversación o ejecución;
- TTL corto;
- alta velocidad;
- naturaleza efímera;
- qué datos mínimos puede contener;
- cuándo se purga.

### 2. Memoria operativa vectorial
Definir:
- documentos indexados para RAG;
- runbooks;
- base de conocimiento del pack;
- materiales del tenant;
- reglas de chunking, embeddings y recuperación;
- separación por tenant.

### 3. Memoria organizacional en grafo
Definir:
- relaciones entre entidades del cliente;
- dependencias operativas;
- CMDB;
- clientes, cuentas, tickets, activos, personas o topologías;
- namespaces por tenant;
- casos donde el grafo sí agrega valor.

### 4. Metadatos relacionales
Definir:
- configuración de tenants;
- billing;
- auditoría;
- esquemas del pack;
- catálogos;
- políticas;
- source of truth transaccional.

### 5. Object storage
Definir:
- documentos originales;
- exports;
- adjuntos;
- respaldos;
- evidencias;
- lifecycle policies;
- cifrado y borrado.

## Qué debe definir el diseño

### 1. Clasificación de datos
Definir:
- dato;
- origen;
- tipo;
- sensibilidad;
- tenant scope;
- persistencia;
- finalidad.

### 2. Estrategia de memoria
Definir:
- qué memoria necesita cada caso de uso;
- qué memoria no necesita;
- qué información se recalcula y cuál se persiste;
- límites de contexto y costo.

### 3. Stores y fuente de verdad
Definir:
- qué vive en Redis o memoria transitoria;
- qué vive en vector store;
- qué vive en grafo;
- qué vive en relacional;
- qué vive en object storage;
- cuál es el source of truth para cada entidad.

### 4. Aislamiento por tenant
Definir:
- colecciones vectoriales separadas;
- namespaces o bases separadas en grafo;
- metadatos y claves de cifrado por tenant;
- restricciones de acceso;
- tagging y trazabilidad por tenant;
- protección contra mezcla accidental.

### 5. Sensibilidad y clasificación
Definir categorías como:
- público;
- interno;
- confidencial;
- regulado;
- PII;
- PHI;
- secreto operativo;
- dato financiero.

### 6. Retención y borrado
Definir:
- tiempos de retención;
- expiración por tipo de dato;
- políticas de archivo;
- borrado lógico y físico;
- evidencias de borrado;
- procesos de derecho al olvido.

### 7. Cifrado y acceso
Definir:
- cifrado en tránsito;
- cifrado en reposo;
- claves por tenant si aplica;
- acceso mínimo necesario;
- segregación de privilegios;
- acceso humano excepcional;
- trazabilidad de acceso.

### 8. Compliance
Definir:
- regulaciones aplicables;
- obligaciones contractuales;
- restricciones por industria;
- necesidad de residencia de datos;
- requerimientos de auditoría;
- requisitos de reporte y evidencias.

### 9. Auditoría del uso de datos
Definir:
- quién accedió;
- qué herramienta accedió;
- qué modelo consumió qué información;
- qué output usó qué fuente;
- qué datos fueron borrados y cuándo;
- qué eventos deben ser inmutables.

## Preguntas guía

### 1. Sobre datos
- ¿Qué datos existen en el caso de uso?
- ¿Qué datos son estructurados y cuáles no?
- ¿Qué datos son source of truth y cuáles solo soporte contextual?
- ¿Qué datos no deberían almacenarse?

### 2. Sobre memoria
- ¿Qué necesita recordar el agente entre pasos?
- ¿Qué necesita recordar entre sesiones?
- ¿Qué conocimiento debe estar disponible por búsqueda?
- ¿Qué relaciones justifican usar grafo?

### 3. Sobre tenant
- ¿Qué debe compartirse globalmente y qué no?
- ¿Cómo evitamos que datos de un tenant aparezcan en otro?
- ¿Qué controles técnicos previenen contaminación entre colecciones o índices?

### 4. Sobre sensibilidad
- ¿Hay PII, PHI, datos financieros o secretos?
- ¿Qué combinaciones de datos elevan el riesgo?
- ¿Qué outputs podrían exponer información sensible?

### 5. Sobre compliance
- ¿Qué norma o exigencia contractual aplica?
- ¿Se requiere derecho al olvido?
- ¿Se requiere residencia local de datos?
- ¿Qué evidencia debe poder entregarse al cliente o auditor?

### 6. Sobre operación
- ¿Quién puede cargar, leer, modificar o borrar información?
- ¿Qué herramientas pueden indexar o consultar memoria?
- ¿Cómo se revoca acceso o se desactiva un tenant?
- ¿Qué sucede con la memoria cuando termina un contrato?

## Salidas esperadas de esta skill

Cuando esta skill responda, debe producir uno o varios de estos artefactos:

### A. Inventario y clasificación de datos
- dato;
- origen;
- tipo;
- sensibilidad;
- tenant scope;
- store;
- retención.

### B. Diseño de memorias
- tipo de memoria;
- finalidad;
- contenido;
- TTL o persistencia;
- store;
- controles.

### C. Mapa de fuentes de verdad
- entidad;
- source of truth;
- réplica o índice derivado;
- observaciones.

### D. Política de aislamiento por tenant
- mecanismo;
- capa afectada;
- control;
- riesgo mitigado.

### E. Política de retención y borrado
- tipo de dato;
- retención;
- trigger de borrado;
- evidencia;
- responsable.

### F. Matriz de compliance
- requisito;
- dato afectado;
- control técnico;
- evidencia;
- observaciones.

### G. Controles de acceso y cifrado
- tipo de acceso;
- actor;
- permiso;
- restricción;
- logging.

### H. Riesgos y mitigaciones
- riesgo;
- impacto;
- probabilidad;
- mitigación;
- residual.

### I. Consumidores del diseño de datos y memoria
- consumidor;
- artefacto consumido;
- decisión habilitada;
- riesgo si falta.

## Criterios de calidad

La skill debe evaluar el diseño usando estos criterios:

- separación correcta entre memorias;
- aislamiento real por tenant;
- trazabilidad del uso de datos;
- minimización de datos;
- claridad de fuentes de verdad;
- cumplimiento de borrado y retención;
- protección de datos sensibles;
- viabilidad operativa para auditoría;
- equilibrio entre utilidad de memoria y riesgo regulatorio.

## Comportamiento esperado del agente

Cuando el usuario quiera guardar todo “por si acaso”, el agente debe forzar minimización y finalidad explícita.  
Cuando una propuesta mezcle conocimiento global del pack con datos del cliente, debe marcarlo como riesgo grave.  
Cuando no exista razón clara para usar vector, grafo o persistencia, debe simplificar.  
Cuando el caso sea regulado, debe endurecer requerimientos de cifrado, acceso, auditoría y residencia de datos.
Cuando una decisión dependa más de control de acceso o de runtime operativo que de taxonomía de datos, debe coordinar con `framework-security` o `framework-platform` en lugar de absorber esa responsabilidad.

## Plantilla de respuesta recomendada

Usa esta estructura:

1. Objetivo de datos y memoria.
2. Clasificación de datos.
3. Diseño de memorias.
4. Fuentes de verdad y stores.
5. Aislamiento por tenant.
6. Sensibilidad, acceso y cifrado.
7. Retención, borrado y derecho al olvido.
8. Compliance y auditoría.
9. Riesgos y trade-offs.
10. Decisiones pendientes.

## Ejemplos de uso

### Ejemplo 1
Consulta: “Diseña memoria y compliance para un pack NOC.”

Respuesta esperada:
- separar runbooks globales del pack frente a tickets y topología del cliente;
- usar sesión, vector y posiblemente grafo según CMDB;
- definir borrado, aislamiento y auditoría por tenant.

### Ejemplo 2
Consulta: “Queremos soportar banca y salud.”

Respuesta esperada:
- elevar clasificación de sensibilidad;
- exigir más controles de acceso, cifrado, auditoría y residencia;
- endurecer guardrails y límites de exposición de datos.

### Ejemplo 3
Consulta: “¿Todo debe ir al vector store?”

Respuesta esperada:
- no;
- separar source of truth transaccional, documentos para RAG y relaciones para grafo;
- justificar cada store por finalidad.

## Checklist final de la skill

Antes de cerrar una respuesta, verificar:

- ¿Se clasificaron los datos?
- ¿Se definieron memorias con finalidad explícita?
- ¿Se asignó un store correcto a cada tipo de información?
- ¿Se resolvió aislamiento por tenant?
- ¿Se definieron cifrado, acceso, retención y borrado?
- ¿Se contempló derecho al olvido o equivalentes?
- ¿Se trazó una matriz de compliance?
- ¿Se indicó qué decisiones continúan en security, platform y core?
- ¿Se documentaron riesgos y mitigaciones?
