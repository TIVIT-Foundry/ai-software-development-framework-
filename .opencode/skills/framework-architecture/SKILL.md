---
name: framework-architecture
description: 'Usa esta skill para transformar la concepción funcional en una arquitectura
  técnica alineada con el framework. Sirve para mapear la solución a las 7 capas,
  definir componentes, contratos, decisiones Build vs Buy, multi-tenancy, routing
  de modelos, memoria, seguridad e infraestructura. Trigger: Cuando ya existe una
  concepción funcional del pack y se necesita mapear la solución a las 7 capas del
  framework.'
version: 1.0
metadata:
  when_to_use:
  - Cuando ya existe una concepción funcional del pack y se necesita aterrizar la
    arquitectura.
  - Cuando se quiere mapear una solución a las 7 capas del framework.
  - Cuando se requiere decidir qué se construye y qué se integra.
  - Cuando se necesita definir contratos entre pack, core, tools, memoria y control.
  - Cuando se prepara la solución para implementación, seguridad, plataforma y QA.
  phase:
  - architecture
  layer:
  - design
  enforcement: mandatory
  depends_on:
  - framework-conception
  - framework-governance
  - framework-pack-design
  consumed_by:
  - framework-core-design
  - framework-data-memory-compliance
  - framework-security
  - framework-platform
  agent_roles:
  - design-agent
  - control-agent
  validation_profile: architecture-consistency
  mcp_usage: none
---

# framework-architecture

## Propósito

Esta skill sirve para diseñar la arquitectura técnica de una solución basada en agentes dentro del framework.  
Su función es traducir una definición funcional en componentes, responsabilidades, contratos, flujos técnicos y decisiones estructurales que permitan construir una solución escalable, portable, segura y gobernable.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Cómo se mapea la solución a las 7 capas del framework?
2. ¿Qué componentes forman la arquitectura y qué responsabilidad tiene cada uno?
3. ¿Qué partes son Build y cuáles Buy?
4. ¿Cómo se resuelve multi-tenancy y aislamiento extremo a extremo?
5. ¿Cómo interactúan pack, core agéntico, modelos, memoria y herramientas?
6. ¿Qué contratos y límites existen entre componentes?
7. ¿Qué capacidades de seguridad, observabilidad y operación deben existir desde el inicio?
8. ¿Cómo se despliega la solución manteniendo portabilidad?

## Relación con otras skills

- `framework-governance` fija principios, restricciones y excepciones que esta skill debe respetar.
- `framework-conception` y `framework-pack-design` aportan la solución funcional y el alcance del producto que esta skill convierte en estructura técnica.
- `framework-architecture` no reemplaza a `framework-core-design`, `framework-data-memory-compliance`, `framework-security` ni `framework-platform`; les reparte responsabilidades, contratos e interfaces.
- `framework-scaffold-implementation` consume esta arquitectura como baseline implementable.

## Qué debe hacer el agente cuando esta skill está activa

El agente debe:

1. Tomar como entrada la concepción funcional del pack.
2. Mapear toda la solución a las 7 capas del framework.
3. Definir componentes principales y responsabilidades técnicas.
4. Identificar contratos entre capas y puntos de integración.
5. Clasificar componentes en Build o Buy.
6. Diseñar el flujo técnico de extremo a extremo.
7. Resolver multi-tenancy, aislamiento y propagación de contexto.
8. Diseñar uso de modelos, memoria, herramientas y observabilidad.
9. Incluir seguridad, trazabilidad y operación como partes nativas de la arquitectura.
10. Producir una arquitectura implementable, no solo conceptual.

## Entradas esperadas

Esta skill asume que ya existe:
- gobierno del framework;
- discovery del vertical;
- concepción funcional;
- definición preliminar del pack y sus casos de uso.

Si estas entradas no existen o están incompletas, la skill debe pedirlas antes de concluir.

## Alcance de la fase

La fase de diseño arquitectónico sí incluye:
- arquitectura por 7 capas;
- componentes y responsabilidades;
- contratos y límites;
- diseño Build vs Buy;
- multi-tenancy;
- routing de modelos;
- memoria y datos;
- seguridad y control;
- observabilidad;
- topología de despliegue;
- decisiones técnicas estructurales.

La fase de diseño arquitectónico no incluye todavía:
- implementación completa;
- configuración final de infraestructura productiva;
- ejecución de pruebas completas;
- operación diaria del sistema.

## Principios que siempre debe respetar

- Arquitectura modular por 7 capas.
- Multi-tenant desde el ingreso.
- Aislamiento estricto entre tenants.
- Core model-agnostic.
- Contrato estable entre pack y core.
- Build para diferenciadores; Buy para commodities.
- Seguridad, trazabilidad y guardrails por defecto.
- Portabilidad de la lógica propia sobre Kubernetes.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- el mapeo a las 7 capas;
- los componentes principales y sus límites;
- los contratos entre capas;
- el reparto de responsabilidades entre pack, core, datos, seguridad y plataforma;
- las decisiones estructurales de Build vs Buy.

Esta skill delega el detalle profundo de cada capa a:
- `framework-core-design` para SDK, runtime y orquestación;
- `framework-data-memory-compliance` para stores, retención, borrado y cumplimiento;
- `framework-security` para RBAC, guardrails, secretos y auditoría;
- `framework-platform` para runtime operativo, observabilidad, CI/CD y resiliencia.

## Mapeo obligatorio a las 7 capas

### 1. Interfaces de Entrada
Definir:
- canales de entrada;
- autenticación y autorización;
- resolución del tenant_id;
- validación y normalización del request;
- rate limiting, WAF y controles de acceso;
- trazabilidad inicial por request.

### 2. Packs Verticales
Definir:
- qué capacidades pertenecen al pack;
- qué agentes encapsula;
- qué integraciones específicas del dominio usa;
- qué conocimiento del vertical contiene;
- cómo se mantiene modular e independiente de otros packs.

### 3. Core Agéntico
Definir:
- SDK o contrato interno;
- orquestación del flujo;
- router model-agnostic;
- catálogo de herramientas;
- manejo de estados, planificación, ejecución y validación;
- trazabilidad técnica del razonamiento.

### 4. Modelos LLM
Definir:
- política de selección de modelos;
- criterios por costo, latencia y sensibilidad;
- fallback automático;
- separación entre modelos frontier, económicos y regulados;
- límites funcionales del uso de modelos.

### 5. Memoria y Datos
Definir:
- memoria de sesión;
- memoria operativa/RAG;
- memoria organizacional/grafo;
- metadatos transaccionales;
- object storage si aplica;
- política de aislamiento, retención, borrado y cifrado.

### 6. Control y Seguridad
Definir:
- trazabilidad;
- guardrails;
- secretos;
- RBAC y políticas;
- auditoría;
- controles por tenant;
- medición y facturación si aplica.

### 7. Infraestructura
Definir:
- cómputo base;
- despliegue sobre Kubernetes;
- workflows largos;
- mensajería;
- observabilidad;
- CI/CD;
- escalado por tenant;
- tagging y costos por workload.

## Preguntas guía

### 1. Sobre la arquitectura general
- ¿Cuáles son los componentes principales?
- ¿Qué responsabilidad tiene cada uno?
- ¿Qué componentes deben ser desacoplados desde el inicio?
- ¿Qué dependencias técnicas son críticas?

### 2. Sobre Build vs Buy
- ¿Qué componente es diferenciador comercial y debe construirse?
- ¿Qué componente ya es commodity y conviene integrar?
- ¿Qué riesgo de lock-in existe en cada decisión?

### 3. Sobre multi-tenancy
- ¿Cómo se resuelve el tenant en el ingreso?
- ¿Cómo se propaga el contexto del tenant entre capas?
- ¿Cómo se garantiza aislamiento en datos, memoria, políticas y operación?

### 4. Sobre el core
- ¿Cómo invoca el pack al core?
- ¿Qué contrato expone el core?
- ¿Cómo se orquesta el flujo del agente?
- ¿Cómo se decide el modelo a usar en cada paso?
- ¿Cómo se exponen herramientas y acciones?

### 5. Sobre modelos
- ¿Qué tipos de modelos participan?
- ¿Cómo se seleccionan por paso?
- ¿Qué fallback existe?
- ¿Qué workloads requieren modelos on-premise o control especial?

### 6. Sobre memoria y datos
- ¿Qué memorias necesita realmente el caso de uso?
- ¿Qué información debe ser persistente?
- ¿Qué datos deben indexarse?
- ¿Qué relaciones requieren grafo?
- ¿Qué datos son source of truth transaccional?

### 7. Sobre seguridad
- ¿Qué secretos existen y cómo se gestionan?
- ¿Qué guardrails se aplican?
- ¿Qué eventos deben quedar auditados?
- ¿Qué políticas de acceso o presupuesto aplican?

### 8. Sobre infraestructura
- ¿Cómo se desplegará la solución?
- ¿Qué partes requieren alta disponibilidad?
- ¿Qué procesos son síncronos y cuáles asíncronos?
- ¿Qué observabilidad mínima debe existir desde el MVP?

## Salidas esperadas de esta skill

Cuando esta skill responda, debe producir uno o varios de estos artefactos:

### A. Arquitectura lógica
- capas;
- componentes;
- responsabilidades;
- relaciones.

### B. Mapa Build vs Buy
- componente;
- categoría;
- justificación;
- riesgo;
- impacto.

### C. Contratos e interfaces
- quién invoca a quién;
- payloads principales;
- eventos relevantes;
- dependencias entre capas.

### D. Flujo técnico end-to-end
- entrada;
- resolución de tenant;
- enrutamiento al pack;
- invocación del core;
- uso de tools/modelos/memoria;
- controles;
- salida;
- trazabilidad.

### E. Diseño de datos y memoria
- tipos de memoria;
- almacenamiento;
- aislamiento;
- retención;
- borrado.

### F. Diseño de seguridad y control
- secretos;
- RBAC;
- políticas;
- guardrails;
- auditoría;
- métricas de uso.

### G. Topología de despliegue
- componentes desplegables;
- dependencias runtime;
- mensajería;
- workflows largos;
- observabilidad;
- CI/CD base.

### H. Lista de ADRs
- decisión;
- contexto;
- alternativas;
- opción elegida;
- impacto.

### I. Mapa de handoff entre skills
- decisión arquitectónica;
- skill dueña del detalle;
- artefacto esperado;
- riesgo si no se aterriza.

### J. Consumidores del diseño arquitectónico
- consumidor;
- artefacto consumido;
- uso esperado;
- riesgo si falta.

## Criterios de calidad arquitectónica

La skill debe evaluar la arquitectura propuesta usando estos criterios:

- alineación con las 7 capas;
- claridad de responsabilidades;
- bajo acoplamiento entre componentes;
- protección contra lock-in;
- soporte real para multi-tenancy;
- seguridad y auditabilidad desde diseño;
- portabilidad;
- facilidad de evolución del pack y del core;
- viabilidad para MVP y escalamiento posterior.

## Comportamiento esperado del agente

Cuando existan varias alternativas, el agente debe compararlas y justificar su recomendación.  
Cuando detecte que una decisión rompe reglas del framework, debe marcarla como excepción y explicar el riesgo.  
Cuando una solución esté sobrediseñada para el MVP, debe proponer una versión arquitectónicamente correcta pero más simple.  
Cuando falte información crítica, debe identificar supuestos abiertos y no fingir precisión.
Cuando una pregunta pertenezca al detalle de core, datos, seguridad o plataforma, debe fijar la decisión arquitectónica y remitir el desarrollo de esa capa a la skill correspondiente.

## Plantilla de respuesta recomendada

Usa esta estructura:

1. Objetivo arquitectónico.
2. Mapeo a las 7 capas.
3. Componentes principales.
4. Decisiones Build vs Buy.
5. Contratos e integraciones.
6. Diseño de modelos, memoria y datos.
7. Diseño de seguridad y control.
8. Infraestructura y operación.
9. Riesgos y trade-offs.
10. Decisiones pendientes.

## Ejemplos de uso

### Ejemplo 1
Consulta: “Ya tenemos la concepción funcional del pack NOC. Ahora define la arquitectura.”

Respuesta esperada:
- mapear ingreso, pack, core, modelos, memoria, control e infraestructura;
- decidir qué componentes son propios;
- definir contratos entre pack y core;
- establecer observabilidad y seguridad mínimas.

### Ejemplo 2
Consulta: “¿Cómo debería quedar la arquitectura de un pack de Customer Engagement?”

Respuesta esperada:
- separar canales de entrada, tools de CRM/knowledge, routing de modelos y guardrails;
- definir qué memoria usa cada caso de uso;
- establecer handoff y trazabilidad.

### Ejemplo 3
Consulta: “Queremos una versión MVP pero sin sobrecargar infraestructura.”

Respuesta esperada:
- mantener principios del framework;
- proponer arquitectura reducida pero válida;
- señalar qué componentes se simplifican sin romper gobierno.

## Checklist final de la skill

Antes de cerrar una respuesta, verificar:

- ¿Se mapeó la solución a las 7 capas?
- ¿Se definieron componentes y responsabilidades?
- ¿Se resolvió Build vs Buy?
- ¿Se resolvió multi-tenancy y aislamiento?
- ¿Se diseñó el flujo pack-core-modelos-tools-memoria?
- ¿Se indicó qué decisiones deben continuar en core, data, security y platform?
- ¿Se incluyeron seguridad, trazabilidad y guardrails?
- ¿Se contempló portabilidad e infraestructura?
- ¿Se documentaron riesgos, trade-offs y decisiones pendientes?
