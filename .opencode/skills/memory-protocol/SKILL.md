---
name: memory-protocol
description: 'Persistent memory protocol for AI agents: structured decisions, bug fixes, discoveries, session lifecycle, progressive disclosure, conflict resolution. Trigger: When implementing agent memory, session persistence, or cross-session knowledge retention.'
version: 1.0
metadata:
  phase:
    - construction
  layer:
    - backend
  enforcement: mandatory
  depends_on:
    - costos-llm
  consumed_by:
    - agent-backend
    - agent-fullstack
  agent_roles:
    - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Define the persistent memory protocol for AI agents in the framework. When an AI agent finishes a session, everything it learned is lost — unless saved. This skill defines the patterns for saving decisions, bug fixes, discoveries, and context across sessions, enabling agents to build cumulative knowledge and avoid repeating mistakes. Inspired by the Engram memory system.

## When to use this skill

Activate this skill when:

- Implementing cross-session agent memory
- Saving important decisions, bug fixes, or pattern discoveries
- Building a knowledge base from agent sessions
- Implementing progressive disclosure of context
- Detecting and resolving conflicting information
- Maintaining session lifecycle (start → work → summary → end)

**Do not** activate when:

- Storing simple key-value cache (use Redis)
- Implementing transactional database operations (use `database-modeling`)
- Building agent tools (use `langchain`)

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `langchain` | Consumidora | Memory Protocol feeds context into LangChain agents |
| `costos-llm` | Complementaria | Memory-aware cost optimization |
| `database-modeling` | Complementaria | pgvector for semantic search over memories |

## Critical Rules

1. **Always save decisions** — Every non-trivial decision must be persisted
2. **Use the structured format** — What / Why / Where / Learned for every memory entry
3. **Progressive disclosure** — search → timeline → detail, never dump all
4. **Session lifecycle mandatory** — Every session starts and ends explicitly
5. **Conflict over blind acceptance** — When two memories contradict, flag for resolution
6. **Deduplicate** — Hash-based dedup in time window, topic_key upserts

## Memory Format

Every memory entry follows this structure:

| Field | Description | Example |
|-------|-------------|---------|
| **What** | The decision, bug, or discovery | "Chose Alembic over Flyway for migrations" |
| **Why** | Reason behind it | "Alembic is Python-native, no JVM dependency" |
| **Where** | Context (file, function, module) | "database-migration skill, migrate_to_postgres()" |
| **Learned** | Takeaway for future sessions | "Always check Alembic version compatibility with SQLAlchemy 2.0" |
| **topic_key** | Stable identifier for upserts | "migration-tool-choice" |
| **confidence** | 0.0-1.0 | 0.95 |
| **tags** | Categorization | ["database", "migration", "decision"] |
| **related** | Links to other memories | ["mem_postgres_setup", "mem_sqlalchemy_config"] |

## When to Save

| Trigger | Priority | Example |
|---------|----------|---------|
| **Decision** | HIGH | Technology choice, architecture trade-off |
| **Bug fix** | HIGH | Non-obvious bug with root cause analysis |
| **Pattern/Discovery** | MEDIUM | "X always fails when Y is configured" |
| **Config/Preference** | LOW | "Tests need `--maxfail=1` on this project" |
| **Session summary** | MANDATORY | Auto-generated at session end |

## Progressive Disclosure

```
Layer 1: mem_search("postgres connection pooling")
         └─> Returns summaries (title + topic_key + confidence)
                ↓
Layer 2: mem_timeline("postgres connection pooling")
         └─> Returns chronological entries with what + where
                ↓
Layer 3: mem_get_observation(mem_id)
         └─> Returns full detail including why + learned + code snippets
```

**Rule:** Agents always start at Layer 1 and only drill deeper if needed. Never load all memories upfront.

## Session Lifecycle

```python
# Session start
async def start_session(project: str, user: str) -> str:
    session_id = str(uuid.uuid4())
    await save_memory(
        what=f"Session started by {user}",
        why="Session lifecycle tracking",
        where=f"project:{project}",
        learned="",
        topic_key=f"session:{session_id}:start",
        tags=["session", "lifecycle"]
    )
    # Pre-load context: recent decisions, project config, active warnings
    await load_session_context(session_id)
    return session_id

# Session work (agent saves as it goes)
async def save_decision(what: str, why: str, where: str, learned: str, 
                         topic_key: str, confidence: float = 0.9):
    await save_memory(what, why, where, learned, topic_key, confidence, 
                      tags=["decision"])

# Session end
async def end_session(session_id: str):
    # Generate summary of all decisions, bugs, discoveries
    summary = await generate_session_summary(session_id)
    await save_memory(
        what=f"Session summary: {summary}",
        why="Session lifecycle tracking",
        where=f"session:{session_id}",
        learned=summary,
        topic_key=f"session:{session_id}:end",
        tags=["session", "summary"]
    )
    # Compact: remove redundant memories
    await compact_session(session_id)
```

## Deduplication

```python
import hashlib
from datetime import datetime, timedelta

WINDOW_HOURS = 24

async def save_or_update_memory(entry: MemoryEntry) -> str:
    # Check for exact duplicate in time window
    content_hash = hashlib.sha256(
        f"{entry.what}{entry.why}{entry.learned}".encode()
    ).hexdigest()
    
    existing = await find_duplicate(content_hash, 
                                     timedelta(hours=WINDOW_HOURS))
    
    if existing:
        # Update metadata, don't create duplicate
        await update_memory_metadata(existing.id, 
                                      confidence=entry.confidence)
        return existing.id
    
    # Check for topic_key upsert
    if entry.topic_key:
        existing_topic = await find_by_topic_key(entry.topic_key)
        if existing_topic:
            # Evolving understanding: increment revision
            await update_memory_content(existing_topic.id, entry,
                                         revision=existing_topic.revision + 1)
            return existing_topic.id
    
    return await insert_memory(entry)
```

## Conflict Detection & Resolution

```python
async def detect_conflicts(new_entry: MemoryEntry) -> list[ConflictPair]:
    # Lexical search for potentially conflicting memories
    candidates = await search_similar(new_entry.what, threshold=0.7)
    
    conflicts = []
    for candidate in candidates:
        if is_lexically_conflicting(new_entry, candidate):
            # Semantic judgment (uses LLM)
            verdict = await judge_conflict(new_entry, candidate)
            conflicts.append(ConflictPair(
                existing=candidate,
                new=new_entry,
                relation=verdict.relation,  # conflicts_with | supersedes | compatible | scoped
                confidence=verdict.confidence,
                reasoning=verdict.reasoning
            ))
    
    return conflicts

class ConflictResolution(Enum):
    CONFLICTS_WITH = "conflicts_with"
    SUPERSEDES = "supersedes"
    COMPATIBLE = "compatible"
    SCOPED = "scoped"  # Different scope, both valid
    NOT_CONFLICT = "not_conflict"
```

## Compaction Recovery

When an agent session is about to hit token limits:

```python
async def compact_and_recover(session_id: str) -> str:
    # 1. Save summary of everything so far
    summary = await generate_session_summary(session_id)
    
    # 2. Get context of most important memories
    context = await get_priority_context(session_id, max_tokens=4000)
    
    # 3. Create recovery prompt for next session
    recovery = f"""Previous session summary: {summary}

Key context for continuity:
{context}

The following decisions are active and must be respected:
{await get_active_decisions(session_id)}

Open issues that need attention:
{await get_open_issues(session_id)}
"""
    
    await save_memory(
        what="Compaction recovery point",
        why="Session was compacted to preserve context",
        where=f"session:{session_id}",
        learned=recovery,
        topic_key=f"session:{session_id}:compact",
        tags=["session", "compaction", "recovery"]
    )
    
    return recovery
```

## Decision table

| Situation | Wrong response | Expected response |
|-----------|---------------|-------------------|
| Agent discovers bug fix | No memory saved | Save with What/Why/Where/Learned |
| Memory contradicts existing | Overwrite blindly | Flag conflict, run judgment |
| Session ending | Nothing | Save summary, compact, generate recovery |
| Token limit approaching | Lose all context | Compact + create recovery point |
| Same decision made again | Create duplicate | Upsert by topic_key, increment revision |

## Verification checklist

- [ ] Memory entries follow What/Why/Where/Learned format
- [ ] Session lifecycle implemented (start/end)
- [ ] Deduplication by content hash + time window
- [ ] Topic keys enable evolutionary upserts
- [ ] Progressive disclosure (3 layers)
- [ ] Conflict detection with lexical + semantic judgment
- [ ] Compaction recovery generates continuity prompts
- [ ] Memories tagged for efficient filtering
