---
name: langfuse
description: 'LLM observability with Langfuse: tracing prompts, generations, costs, feedback loops, and evaluation datasets. Trigger: When adding observability to LLM workflows, agent traces, or cost attribution.'
version: 1.0
metadata:
  phase:
    - construction
    - operations
  layer:
    - backend
  enforcement: recommended
  depends_on:
    - observabilidad
    - costos-llm
  consumed_by:
    - langchain
    - framework-core-design
  agent_roles:
    - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Define how Langfuse is integrated to trace LLM calls, monitor prompt versions, attribute costs per tenant/feature, and collect feedback for evaluation.

## When to use this skill

Activate when:
- Building agentic workflows with LangChain/LangGraph
- Need cost attribution per tenant or feature
- Collecting human feedback on LLM outputs

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `costos-llm` | sibling | Cost attribution |
| `langchain` | consumer | Instrumentation target |
| `observabilidad` | parent | Generic observability |

## Critical Rules

1. Initialize Langfuse with environment variables (`LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`).
2. Trace every LLM call with `trace`, `span`, `generation` structure.
3. Tag traces with `tenant_id`, `feature`, `model`, `version`.
4. Do not log PII or secrets in prompts/metadata.
5. Use scores/feedback to build evaluation datasets.

## Outputs produced

| Artifact | Path | Description |
|----------|------|-------------|
| Client | `src/shared/langfuse_client.py` / `langfuse.ts` | Langfuse client wrapper |
| Callback | `src/shared/langfuse_callback.*` | LangChain callback |
| Dashboard config | `observability/langfuse/` | Score configs, datasets |

## Example: LangChain callback

```python
from langfuse.callback import CallbackHandler
langfuse_handler = CallbackHandler()

chain.invoke({"query": user_input}, config={"callbacks": [langfuse_handler]})
```

## Checklist

- [ ] Langfuse credentials in environment variables
- [ ] Callback handler wired to LangChain/LangGraph
- [ ] Traces tagged with tenant and feature
- [ ] PII excluded from prompts
- [ ] Feedback scores collected for critical flows
