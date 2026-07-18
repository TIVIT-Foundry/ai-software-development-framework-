---
name: framework-operations-evolution
description: 'Usa esta skill para diseñar la operación y evolución del framework.
  Sirve para definir monitoreo, soporte, incidentes, SLOs, versionado, deprecación,
  backward compatibility, gestión de cambios y ciclo de mejora continua. Trigger:
  Cuando el framework ya está en uso y se necesita diseñar operación, SLOs, versionado,
  deprecación y mejora continua.'
version: 1.0
metadata:
  when_to_use:
  - Cuando el framework ya está en uso y se necesita operación continua.
  - Cuando se quiere definir cómo se atienden incidentes y degradaciones.
  - Cuando se debe sostener evolución sin romper packs ni contratos.
  - Cuando se necesita diseñar versionado, deprecación y compatibilidad.
  - Cuando se quiere cerrar el ciclo entre producción, feedback y roadmap.
  phase:
  - operations
  layer:
  - operations
  enforcement: mandatory
  depends_on:
  - framework-platform
  - framework-qa-validation
  consumed_by:
  - framework-governance
  - framework-architecture
  - pull-request
  agent_roles:
  - delivery-agent
  - control-agent
  validation_profile: documentation
  mcp_usage: optional
---

# framework-operations-evolution

## Propósito

Esta skill sirve para diseñar la operación sostenida y la evolución del framework a lo largo del tiempo.  
Su función es definir cómo se monitorea el sistema, cómo se atienden incidentes, cómo se introducen cambios, cómo se versionan contratos y cómo se mantiene compatibilidad mientras el framework crece.

La observabilidad base nace en `framework-platform`, pero esta skill define cómo esa observabilidad se convierte en operación accionable, ownership, escalamiento y aprendizaje para la evolución del framework.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Cómo se monitorea la salud del framework en producción?
2. ¿Cómo se atienden incidentes, degradaciones y fallos?
3. ¿Cómo se priorizan parches, mejoras y nuevas capacidades?
4. ¿Cómo se versionan el SDK, el core y los packs?
5. ¿Cómo se deprecian componentes sin romper clientes?
6. ¿Qué política de backward compatibility se aplica?
7. ¿Cómo se mide adopción, uso, costo y estabilidad?
8. ¿Cómo se convierte la operación en insumo para la siguiente iteración?

## Relación con otras skills

- `framework-platform` define la base técnica de observabilidad, despliegue y resiliencia que esta skill opera.
- `framework-qa-validation` aporta evidencia y gating para releases, regresiones y compatibilidad.
- `framework-governance` define el baseline y las excepciones para cambios mayores.
- `framework-operations-evolution` devuelve aprendizaje y necesidades de cambio hacia governance, architecture y roadmap.

## Qué debe hacer el agente cuando esta skill está activa

El agente debe:

1. Diseñar el modelo de operación continua.
2. Definir monitoreo, alertas, SLOs y umbrales.
3. Diseñar el manejo de incidentes y escalamiento.
4. Definir el proceso de releases y hotfixes.
5. Diseñar versionado semántico y compatibilidad hacia atrás.
6. Definir políticas de deprecación y migración.
7. Diseñar mecanismos para recopilar feedback operativo.
8. Establecer métricas de salud, adopción, costo y valor.
9. Mantener estabilidad del contrato con packs y clientes.
10. Evitar que la evolución técnica rompa la propuesta comercial.

## Entradas esperadas

Esta skill asume que ya existe:
- arquitectura general;
- reglas de governance para cambios y excepciones;
- scaffold o implementación;
- QA y validación;
- plataforma e infraestructura;
- observabilidad base.

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase de operación y evolución sí incluye:
- monitoreo continuo;
- alertas;
- incident response;
- soporte;
- mantenimiento;
- release management;
- hotfixes;
- versionado;
- deprecación;
- compatibilidad;
- feedback loop;
- roadmap evolution.

La fase de operación y evolución no incluye todavía:
- rediseño total de arquitectura;
- cambios de propósito del framework;
- reestructuración radical del core sin justificación;
- procesos corporativos ajenos al producto.

## Principios que siempre debe respetar

- La operación debe ser observable y accionable.
- El incidente es un proceso, no una improvisación.
- La estabilidad del contrato vale más que la velocidad de cambio.
- Cambios incompatibles deben ser raros, explícitos y migrables.
- La evolución debe reducir deuda, no expandirla.
- La producción es una fuente de aprendizaje formal.
- Lo que se depreca debe tener ruta clara de salida.
- La mejora continua debe proteger a packs y clientes existentes.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- el modelo operativo continuo;
- el proceso de incidentes, releases y hotfixes;
- la política de versionado, compatibilidad y deprecación;
- qué señales operativas retroalimentan la evolución del framework.

Esta skill delega:
- la observabilidad base y la plataforma técnica a `framework-platform`;
- la evidencia de validación a `framework-qa-validation`;
- cambios estructurales del framework a governance y architecture cuando correspondan.

## Qué debe definir el diseño

### 1. Modelo operativo
Definir:
- quién opera;
- qué monitorea;
- qué umbrales existen;
- qué se considera degradación;
- qué se considera incidente;
- qué se considera emergencia.

### 2. Observabilidad en operación
Definir:
- métricas;
- logs;
- traces;
- dashboards;
- alertas;
- SLOs;
- error budgets;
- alert routing;
- qué señales vienen de plataforma y cuáles son responsabilidad operativa del framework.

### 3. Gestión de incidentes
Definir:
- detección;
- triage;
- severidad;
- escalamiento;
- comunicación;
- mitigación;
- postmortem;
- acciones preventivas.

### 4. Releases y hotfixes
Definir:
- frecuencia de release;
- caminos de promoción;
- hotfix vs release normal;
- rollback;
- canary;
- feature flags;
- validación post-release.

### 5. Versionado
Definir:
- versionado semántico;
- versionado del SDK;
- versionado del core;
- versionado de packs;
- compatibilidad entre versiones;
- política de cambios mayores, menores y parches.

### 6. Backward compatibility
Definir:
- qué contratos no pueden romperse;
- cómo se anuncian cambios;
- cuánto tiempo vive una versión anterior;
- cómo se validan migraciones;
- cómo se apagan versiones viejas.

### 7. Deprecación
Definir:
- criterios para deprecación;
- aviso previo;
- ventanas de transición;
- mecanismos de migración;
- control de fin de vida;
- evidencia de adopción de la nueva versión.

### 8. Feedback operativo
Definir:
- qué señales vienen de producción;
- qué métricas ayudan a priorizar producto;
- qué fallos indican deuda de diseño;
- cómo se retroalimenta el roadmap.

### 9. Métricas de evolución
Definir:
- adopción por pack;
- frecuencia de uso;
- costo por tenant;
- estabilidad por versión;
- latencia;
- tasa de incidentes;
- tiempo de recuperación;
- satisfacción operativa.

### 10. Gobernanza del cambio
Definir:
- quién aprueba cambios que rompen compatibilidad;
- quién aprueba cambios de infraestructura relevante;
- qué cambios exigen comunicación a clientes;
- qué cambios requieren migración guiada.

Cambios mayores en SDK, core, seguridad o modelo operativo deben escalar a `framework-governance` para validación de excepción o actualización del baseline.

## Preguntas guía

### 1. Sobre operación
- ¿Qué indicadores dicen que el framework está sano?
- ¿Quién responde si un pack o el core falla?
- ¿Qué se monitoriza a nivel plataforma versus producto?

### 2. Sobre incidentes
- ¿Qué diferencia un bug de un incidente?
- ¿Qué severidades definimos?
- ¿Cómo se notifica al equipo y al cliente?

### 3. Sobre cambios
- ¿Con qué frecuencia se libera?
- ¿Qué validación requiere un hotfix?
- ¿Qué cambios pueden entrar sin migración?

### 4. Sobre compatibilidad
- ¿Qué contratos deben protegerse por años?
- ¿Qué parte del SDK puede evolucionar sin afectar packs?
- ¿Cómo garantizamos que un pack viejo siga funcionando?

### 5. Sobre deprecación
- ¿Qué hacemos con funcionalidades obsoletas?
- ¿Cuánto tiempo avisamos antes de retirar algo?
- ¿Cómo medimos si los clientes ya migraron?

### 6. Sobre aprendizaje
- ¿Qué errores recurrentes revelan problemas de diseño?
- ¿Qué costos operativos indican necesidad de optimizar?
- ¿Qué señales de producción deben volver al backlog?

## Salidas esperadas de esta skill

Cuando esta skill responda, debe producir uno o varios de estos artefactos:

### A. Modelo operativo
- rol;
- responsabilidad;
- sistema monitoreado;
- umbral;
- acción.

### B. Estrategia de observabilidad
- métrica;
- fuente;
- umbral;
- alerta;
- dashboard.

Debe indicar además:
- dueño operativo;
- severidad asociada;
- acción esperada.

### C. Procedimiento de incidentes
- severidad;
- paso;
- responsable;
- comunicación;
- resolución.

### D. Plan de releases
- tipo;
- frecuencia;
- validaciones;
- rollback;
- evidencias.

### E. Esquema de versionado
- componente;
- tipo de versión;
- compatibilidad;
- política de cambio.

### F. Política de deprecación
- elemento;
- aviso;
- fecha objetivo;
- ruta de migración;
- estado.

### G. Matriz de compatibilidad
- versión origen;
- versión destino;
- compatible sí/no;
- comentario.

### H. Métricas de evolución
- KPI;
- definición;
- frecuencia;
- uso en decisión.

### I. Consumidores de operación y evolución
- consumidor;
- evidencia o política consumida;
- decisión habilitada;
- riesgo si falta.

## Criterios de calidad

La skill debe evaluar el diseño usando estos criterios:

- operación clara y responsable;
- observabilidad útil y accionable;
- incidentes tratados de forma estándar;
- releases seguros;
- versionado consistente;
- compatibilidad protegida;
- deprecación planificada;
- retroalimentación real desde producción;
- evolución sin romper la base.

## Comportamiento esperado del agente

Cuando una propuesta de cambio rompa contratos sin plan, el agente debe marcarlo como alto riesgo.  
Cuando no exista ruta de deprecación, debe considerarlo incompleto.  
Cuando la operación dependa de conocimiento tácito, debe formalizarlo.  
Cuando la estabilidad perjudique toda evolución, debe buscar un equilibrio con versionado y migración guiada.
Cuando una señal exista en platform pero no tenga dueño, umbral ni respuesta operativa, debe tratarla como observabilidad incompleta.

## Plantilla de respuesta recomendada

Usa esta estructura:

1. Objetivo de operación y evolución.
2. Modelo operativo.
3. Observabilidad y SLOs.
4. Gestión de incidentes.
5. Releases y hotfixes.
6. Versionado y compatibilidad.
7. Deprecación y migración.
8. Métricas de evolución.
9. Riesgos y trade-offs.
10. Roadmap de mejora.

## Ejemplos de uso

### Ejemplo 1
Consulta: “¿Cómo operamos el framework en producción?”

Respuesta esperada:
- modelo operativo;
- monitoreo;
- alertas;
- incident response;
- comunicación;
- postmortem.

### Ejemplo 2
Consulta: “Queremos cambiar el SDK sin romper packs viejos.”

Respuesta esperada:
- versionado semántico;
- contract tests;
- backward compatibility;
- deprecación gradual;
- migración guiada.

### Ejemplo 3
Consulta: “Necesitamos plan de evolución trimestral.”

Respuesta esperada:
- métricas de adopción y estabilidad;
- priorización por impacto operativo;
- roadmap incremental con control de compatibilidad.

## Checklist final de la skill

Antes de cerrar una respuesta, verificar:

- ¿Se definió operación continua?
- ¿Se cubrieron incidentes y escalamiento?
- ¿Se establecieron SLOs y alertas?
- ¿Se diseñaron releases y hotfixes?
- ¿Se protegió backward compatibility?
- ¿Hay política de deprecación?
- ¿Se distinguió qué parte de la observabilidad pertenece a platform y cuál a operations?
- ¿La evolución retroalimenta producto?
- ¿Se preserva el contrato con packs y clientes?
