---
name: framework-extensions
description: 'Extension system for the framework: plugin architecture, manifest schema, hooks, priority stack, catalog management. Trigger: When creating framework extensions, building plugins, or extending framework capabilities with community contributions.'
version: 1.0
metadata:
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
  validation_profile: architecture
  mcp_usage: none
---

## Purpose

Define the extension system for the framework. Extensions are installable plugins that add capabilities (commands, skills, templates, hooks) without modifying the core. Modeled after the Spec Kit extension system, this skill enables a plugin ecosystem where community and team contributions extend the framework's reach while maintaining the core's integrity.

## When to use this skill

Activate this skill when:

- Creating a new extension for the framework
- Installing or configuring extensions
- Building a plugin ecosystem around the framework
- Contributing community extensions
- Managing extension catalogs (discovery, installation, updates)

**Do not** activate when:

- Modifying core framework skills (those are skills, not extensions)
- Creating a single reusable component (that's a shared library)
- Configuring CI/CD (use `ci-cd`)

## Extension Manifest Schema

Every extension defines an `extension.yml`:

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

## Extension Architecture

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

## Priority Stack

Extensions resolve with priority:

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

## Hook System

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

## Catalog System

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

## CLI Commands for Extension Management

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

## Creating an Extension

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

**Example command template (`commands/hello.md`):**
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

## When NOT to Create an Extension

| Situation | Should be an extension? | Alternative |
|-----------|------------------------|-------------|
| One team needs it | No | Project-local override |
| Core framework functionality | No | Contribute to core or create a skill |
| Purely configuration | No | Preset |
| Single command, no hooks | No | Just create the command in project |
| Multi-team, reusable, with hooks | YES | Extension |

## Decision table

| Situation | Wrong response | Expected response |
|-----------|---------------|-------------------|
| Need a custom deploy step | Modify core | Create an extension with hooks |
| Extension conflicts with core | Let it break | Priority stack resolves automatically |
| Community extension is risky | Install anyway | Check policy (discovery-only vs install-allowed) |
| Need to chain extensions | Install them individually | Use workflow to orchestrate extension hooks |

## Verification checklist

- [ ] Extension manifest valid (`extension.yml` schema)
- [ ] Hook handlers have timeout protection
- [ ] Catalog entries have correct policy tags
- [ ] Priority stack resolves correctly (project > preset > installed > builtin)
- [ ] Extensions don't modify core framework files
- [ ] Community catalog maintained and reviewed
