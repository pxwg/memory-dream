---
name: memory-dream-coding
description: Use project-local Memory Dream during coding work. Trigger when Codex should load project memory before implementation, keep Memory.md artifacts current, record lightweight decision or experience notes, link notes into the project memory entry point, or update memory at the end of a coding task using the memory-dream CLI.
---

# Memory Dream Coding

Use `memory-dream` as the only interface to project memory. Do not edit generated artifacts under `artifact/`; write memory through source notes and `index.typ` via the CLI.

## Start Of Work

1. Run `memory-dream status --format json`.
2. If `status` reports an unregistered project, run `memory-dream init`, then rerun `status`.
3. If `built` is false or `stale` is true, run `memory-dream build`.
4. Run `memory-dream context` and use that output as the default project memory context.

If `memory-dream context` reports stale or missing artifacts, run `memory-dream build` once and retry `context`.

## During Coding

Prefer reading memory through:

```bash
memory-dream context
memory-dream list --format json
memory-dream edit <id>
```

`memory-dream edit <id>` prints the source note path by default. Read or patch that source file only when the task requires direct note editing. Do not patch `artifact/Memory.md` or `artifact/memory/*.md`.

## Recording Lightweight Memory

At the end of a task, write memory only when there is durable value:

- `decision`: architectural choices, API contracts, project conventions, rejected alternatives.
- `experience`: debugging lessons, workflow gotchas, integration behavior, test or release knowledge.

Use concise titles. One note should capture one reusable idea.

Create linked, immediately consumable memory with:

```bash
memory-dream new --title "<title>" --kind decision --content "<body>" --link --build
memory-dream new --title "<title>" --kind experience --content "<body>" --link --build
```

Use `--link --build` when the note should appear in future `memory-dream context`. Omit `--link` for scratch notes that should not enter default AI context yet.

## Updating Existing Notes

1. Use `memory-dream list --format json` to find candidate IDs.
2. Use `memory-dream edit <id>` to get the source path.
3. Edit the source note, preserving the existing note ID and heading.
4. Run `memory-dream build`.
5. Run `memory-dream context` to verify the memory is consumable.

## Link Existing Notes

If a useful note exists but is not in default context:

```bash
memory-dream link <id> --build
```

`link` is idempotent and appends the note reference to `index.typ`.

## Guardrails

- Do not write memory for trivial implementation details that are obvious from code.
- Do not store secrets, tokens, private credentials, or transient logs.
- Keep note content factual and project-specific.
- Prefer one durable note over many low-signal notes.
- Treat `Memory.md` as generated output; source of truth is the managed zk-lsp wiki under the registered memory source path.
