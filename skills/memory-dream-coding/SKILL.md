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

Create ordinary coding memory with:

```bash
memory-dream new --title "<title>" --kind decision --content "<body>" --build
memory-dream new --title "<title>" --kind experience --content "<body>" --build
```

Do not link routine coding notes into `Memory.md` by default. Linking changes the project-level memory entry point and should usually be left to curation. Use `--link --build` only when the user explicitly asks to promote the note or when the note is clearly an entry-level project decision that future agents must see immediately.

## Updating Existing Notes

1. Use `memory-dream list --format json` to find candidate IDs.
2. Use `memory-dream edit <id>` to get the source path.
3. Edit the source note, preserving the existing note ID and heading.
4. Run `memory-dream build`.
5. Run `memory-dream context` to verify the memory is consumable.

## Link Existing Notes Sparingly

If the user explicitly asks to promote a useful note into default context:

```bash
memory-dream link <id> --build
```

`link` is idempotent and appends the note reference to `index.typ`. Do not use it as a routine end-of-task step.

## Guardrails

- Do not write memory for trivial implementation details that are obvious from code.
- Do not store secrets, tokens, private credentials, or transient logs.
- Keep note content factual and project-specific.
- Prefer one durable note over many low-signal notes.
- Treat `Memory.md` as generated output; source of truth is the managed zk-lsp wiki under the registered memory source path.
