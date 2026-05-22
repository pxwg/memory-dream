---
name: memory-dream-reader
description: Read Memory Dream project memory and build task-specific context without editing memory. Trigger when Codex needs to query Memory.md, follow linked memory cards, retrieve relevant decisions, experiences, user preferences, workflows, constraints, or project facts, and return a compact memory bundle for the current task.
---

# Memory Dream Reader

Use this skill to retrieve relevant project memory without writing memory. It is for context building, not curation.

## Read-Only Contract

Allowed:

- `memory-dream status --format json`
- `memory-dream build` when artifacts are missing or stale
- `memory-dream context`
- `memory-dream context --all`
- `memory-dream list --format json`
- `memory-dream edit <id>` to locate and read source notes
- read files under the managed source wiki and artifact directory

Forbidden:

- `memory-dream new`
- `memory-dream link`
- direct edits
- lifecycle or metadata changes
- git commits
- changing `index.typ`

## Workflow

1. Run `memory-dream status --format json`.
2. If artifacts are missing or stale, run `memory-dream build`.
3. Run `memory-dream context` to read the bootloader and entry notes.
4. Identify which entry links, decisions, experiences, operations, preferences, or constraints are relevant to the current task.
5. Follow only relevant links. Use `memory-dream context --all` only when the query cannot be answered from the default context.
6. Use `memory-dream edit <id>` only to locate source notes that must be read directly.
7. Return a compact memory bundle, not raw full-context dumps.

## Delegation

If the main task is simple, the main agent can use this skill locally.

If the memory query may require following several links, comparing notes, or compressing a large memory graph, and the user has authorized subagents, delegate to a read-only memory subagent. The subagent should return only the task-relevant memory bundle and the note IDs consulted.

## Output Shape

Return:

```markdown
## Memory Query Result

### Relevant Operating Rules
- ...

### Relevant Decisions
- ...

### Relevant Experiences Or Preferences
- ...

### Source Notes Consulted
- 2605221059 Title

### Gaps Or Uncertainty
- ...
```

Omit empty sections. Keep the output short enough to be pasted into the main task context.

## Guardrails

- Prefer semantic links over scanning every note.
- Do not treat generated artifacts as source of truth when source notes are needed.
- Do not mutate memory while reading.
- Do not summarize unsupported claims as memory.
- Preserve distinction between project facts, user preferences, and inferred guidance.
