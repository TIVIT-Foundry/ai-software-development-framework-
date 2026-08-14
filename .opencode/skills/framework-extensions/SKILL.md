---
name: framework-extensions
description: 'Sistema de extensiones del framework: arquitectura de plugins, schema del manifest, hooks, pila de prioridades, gestión de catálogo. Trigger: Cuando se crean extensiones del framework, se construyen plugins o se extienden capacidades con contribuciones de la comunidad.'
version: 1.2
metadata:
  when_to_use:
  - Cuando se necesita crear una extensión o plugin del framework.
  - Cuando se define el schema del manifest o se gestiona el catálogo de extensiones.
  phase:
    - construction
  layer:
    - implementation
  enforcement: recommended
  depends_on:
    - project-architecture
  consumed_by:
    - agent-backend
  agent_roles:
    - delivery-agent
    - design-agent
  validation_profile: documentation
  mcp_usage: none
---

## Propósito

Define el sistema de extensiones del framework. Las extensiones son plugins instalables que añaden capacidades (comandos, skills, templates, hooks) sin modificar el core. Inspirado en el sistema de extensiones de Spec Kit, esta skill habilita un ecosistema de plugins donde las contribuciones de la comunidad y del equipo extienden el alcance del framework mientras se mantiene la integridad del core.

## Cuándo usar esta skill

Activa esta skill cuando:

- Al crear una nueva extensión del framework
- Al instalar o configurar extensiones
- Al construir un ecosistema de plugins alrededor del framework
- Al contribuir extensiones de la comunidad
- Al gestionar catálogos de extensiones (discovery, instalación, actualizaciones)

**No** la actives cuando:

- Al modificar skills del core del framework (esas son skills, no extensiones)
- Al crear un componente reutilizable único (eso es una shared library)
- Al configurar CI/CD (usa `ci-cd`)

## Schema del Manifest de extensiones

Cada extensión define un `extension.yml`:

```yaml
schema_version: "1.0"
extension:
  id: "my-extension"              # Unique identifier
  name: "My Extension"            # Human-readable name
  version: "1.0.0"               # Semantic versioning
  description: "What this extension does"
  author: "Team/Organization"
  repository: "https://github.com/org/my-extension"
  license: "MIT"
  tags:
    - backend
    - automation

requires:
  framework_version: ">=2.0"
  tools:
    - python: ">=3.12"
  skills:
    - backend-api
    - database-modeling

provides:
  commands:
    - name: deploy
      file: commands/deploy.md
      description: "Deploy the application to staging"
  skills:
    - path: skills/custom-auth
  templates:
    - name: docker-compose.prod
      path: templates/docker-compose.prod.yml
      description: "Production docker-compose with monitoring"
  config:
    - name: deploy.env
      template: templates/deploy.env.example
      description: "Deployment configuration variables"

hooks:
  before_build:
    command: hooks/validate-env
    optional: false
    description: "Validate environment before build"
  after_deploy:
    command: hooks/health-check
    optional: true
    description: "Health check after deployment"

# Phases where this extension injects behavior
sd_phases:
  - scaffold
  - construction
  - operations
```

## Arquitectura de extensiones

```
framework-extensions/
├── catalog.json              # Built-in extension catalog
├── catalog.community.json    # Community extension catalog
├── my-extension/
│   ├── extension.yml         # Manifest
│   ├── commands/             # Slash commands (*.md)
│   ├── skills/               # Additional skills
│   ├── templates/            # Reusable templates
│   ├── hooks/                # Hook scripts
│   └── README.md
└── ...
```

## Pila de prioridades

Las extensiones se resuelven con esta prioridad:

```
1. Project-Local Overrides (project/.extensions/)
2. Presets (preset configuration)
3. Installed Extensions (installed via CLI)
4. Built-in Extensions (framework core)
```

```python
class ExtensionStack:
    """Resolve extensions with priority ordering."""
    
    def __init__(self):
        self.layers = [
            ProjectLocalLayer(),   # Highest priority
            PresetLayer(),
            InstalledLayer(),
            BuiltinLayer()         # Lowest priority
        ]
    
    def resolve(self, command_name: str) -> Command | None:
        for layer in self.layers:
            command = layer.find_command(command_name)
            if command:
                return command
        return None
    
    def resolve_all(self, command_name: str) -> list[Command]:
        """Get all matching commands across layers."""
        commands = []
        for layer in self.layers:
            cmd = layer.find_command(command_name)
            if cmd:
                commands.append(cmd)
        return commands
```

## Sistema de hooks

```python
from enum import Enum
from dataclasses import dataclass
from typing import Callable

class HookPoint(Enum):
    BEFORE_CONSTITUTION = "before_constitution"
    AFTER_CONSTITUTION = "after_constitution"
    BEFORE_SPECIFY = "before_specify"
    AFTER_SPECIFY = "after_specify"
    BEFORE_PLAN = "before_plan"
    AFTER_PLAN = "after_plan"
    BEFORE_TASKS = "before_tasks"
    AFTER_TASKS = "after_tasks"
    BEFORE_IMPLEMENT = "before_implement"
    AFTER_IMPLEMENT = "after_implement"
    BEFORE_DEPLOY = "before_deploy"
    AFTER_DEPLOY = "after_deploy"

@dataclass
class Hook:
    name: str
    hook_point: HookPoint
    handler: Callable
    optional: bool = True
    timeout_seconds: int = 30

class HookManager:
    def __init__(self):
        self.hooks: dict[HookPoint, list[Hook]] = {}
    
    def register(self, extension_id: str, hook: Hook):
        if hook.hook_point not in self.hooks:
            self.hooks[hook.hook_point] = []
        self.hooks[hook.hook_point].append(hook)
    
    async def execute(self, hook_point: HookPoint, context: dict) -> list[HookResult]:
        results = []
        for hook in self.hooks.get(hook_point, []):
            try:
                result = await asyncio.wait_for(
                    hook.handler(context),
                    timeout=hook.timeout_seconds
                )
                results.append(HookResult(hook.name, True, result))
            except asyncio.TimeoutError:
                if not hook.optional:
                    raise HookTimeoutError(f"Hook {hook.name} timed out")
                results.append(HookResult(hook.name, False, "timeout"))
            except Exception as e:
                if not hook.optional:
                    raise HookExecutionError(f"Hook {hook.name} failed: {e}")
                results.append(HookResult(hook.name, False, str(e)))
        return results
```

## Sistema de catálogo

```json
{
  "schema_version": "1.0",
  "updated_at": "2026-07-17T00:00:00Z",
  "catalog_url": "https://framework.extensions/catalog.json",
  "extensions": {
    "git-workflow": {
      "id": "git-workflow",
      "name": "Git Workflow Extension",
      "version": "1.0.0",
      "description": "Automated branching and commit hooks for SDD phases",
      "author": "Framework Team",
      "repository": "https://github.com/org/git-workflow-ext",
      "tags": ["git", "automation", "workflow"],
      "policy": "install-allowed"
    },
    "community-ci-templates": {
      "id": "community-ci-templates",
      "name": "Community CI Templates",
      "version": "0.5.0",
      "description": "Community-contributed CI pipeline templates",
      "author": "Community",
      "repository": "https://github.com/community/ci-templates",
      "tags": ["ci", "community"],
      "policy": "discovery-only"
    }
  }
}
```

## Comandos CLI para la gestión de extensiones

```python
# Install an extension
specify extension add git-workflow

# List installed extensions
specify extension list

# Show extension details
specify extension info git-workflow

# Update extension to latest
specify extension update git-workflow

# Remove extension
specify extension remove git-workflow

# Search for extensions
specify extension search "git"

# Validate extension manifest
specify extension validate ./my-extension
```

## Crear una extensión

```bash
# Scaffold a new extension
specify extension create my-first-extension

# This creates:
my-first-extension/
├── extension.yml
├── commands/
│   └── hello.md
├── skills/
├── templates/
├── hooks/
└── README.md
```

**Ejemplo de plantilla de comando (`commands/hello.md`):**
```markdown
---
description: "Greet the user with a friendly message"
handoffs:
  - label: "Proceed to specify phase"
    agent: design
    command: specify
---

## Command: /hello

Activate when the user wants a greeting.

### Workflow

1. Ask the user for their name
2. Greet them with a personalized message
3. Offer to proceed to the specify phase

### Validation

- Name must not be empty
- Name must be <100 characters
```

## Cuándo NO crear una extensión

| Situación | ¿Debe ser una extensión? | Alternativa |
|-----------|------------------------|-------------|
| Solo un equipo la necesita | No | Override local del proyecto |
| Funcionalidad del core del framework | No | Contribuir al core o crear una skill |
| Configuración pura | No | Preset |
| Comando único, sin hooks | No | Crear el comando directamente en el proyecto |
| Multi-equipo, reutilizable, con hooks | SÍ | Extensión |

## Tabla de decisiones

| Situación | Respuesta incorrecta | Respuesta esperada |
|-----------|---------------|-------------------|
| Se necesita un paso de deploy personalizado | Modificar el core | Crear una extensión con hooks |
| La extensión entra en conflicto con el core | Dejar que se rompa | La pila de prioridades resuelve automáticamente |
| Una extensión de la comunidad es riesgosa | Instalarla igual | Revisar la política (discovery-only vs install-allowed) |
| Se necesitan encadenar extensiones | Instalarlas individualmente | Usar el workflow para orquestar los hooks de las extensiones |

## Checklist de verificación

- [ ] Manifest de la extensión válido (schema de `extension.yml`)
- [ ] Los handlers de hooks tienen protección por timeout
- [ ] Las entradas del catálogo tienen los policy tags correctos
- [ ] La pila de prioridades resuelve correctamente (project > preset > installed > builtin)
- [ ] Las extensiones no modifican archivos del core del framework
- [ ] El catálogo de la comunidad se mantiene y se revisa
