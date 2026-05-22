---
name: memory-dream-project
description: Use project-local Memory Dream during any project work session, including code, writing, research, physical notes, creative projects, planning, or user workflow capture. Trigger when Codex should load project memory, preserve user operations or preferences, record lightweight decisions or experiences, keep Memory.md artifacts current, or update project memory using the memory-dream CLI.
---

# Memory Dream Project

Use `memory-dream` as the interface to project memory. Do not edit generated artifacts under `artifact/`; write memory through source notes and `index.typ` via the CLI or source wiki.

## Start Of Work

1. Run `memory-dream status --format json`.
2. If `status` reports an unregistered project, run `memory-dream init`, then rerun `status`.
3. If `built` is false or `stale` is true, run `memory-dream build`.
4. Run `memory-dream context` and use that output as the default project memory context.

If `memory-dream context` reports stale or missing artifacts, run `memory-dream build` once and retry `context`.

## During The Session

Prefer reading memory through:

```bash
memory-dream context
memory-dream list --format json
memory-dream edit <id>
```

`memory-dream edit <id>` prints the source note path by default. Read or patch that source file only when the task requires direct note editing. Do not patch `artifact/Memory.md` or `artifact/memory/*.md`.

Treat `Memory.md` as an agent bootloader: it should orient behavior and route to high-value entry cards, not become a long README or a dump of every note. Normal project work should preserve that shape.

## Recording Lightweight Memory

At the end of a session, write memory only when there is durable value:

- `decision`: project choices, constraints, conventions, rules, worldbuilding facts, research conclusions, planning commitments, rejected alternatives.
- `experience`: user workflows, operating preferences, repeated procedures, lessons learned, tool behavior, physical-process notes, creative process observations.

Use concise titles. One note should capture one reusable idea.

Create ordinary project memory with:

```bash
memory-dream new --title "<title>" --kind decision --content "<body>" --build
memory-dream new --title "<title>" --kind experience --content "<body>" --build
```

Do not link routine session notes into `Memory.md` by default. Linking changes the project-level memory entry point and should usually be left to curation. Use `--link --build` only when the user explicitly asks to promote the note or when the note is clearly an entry-level project fact that future agents must see immediately.

## Git Audit Trail

The managed source wiki is a git repository. When the environment supports subagents, delegate memory writing to a dedicated memory-writing agent instead of mixing project work and memory edits in the same agent flow.

The memory-writing agent should:

1. Run `memory-dream open` to locate the source wiki.
2. Create or update source notes through `memory-dream`/`zk-lsp`.
3. Run `memory-dream build` and `memory-dream context` for verification.
4. Commit only the memory source/wiki changes inside the source wiki git repo.
5. Use Conventional Commits, for example `docs(memory): record archive workflow` or `chore(memory): add user preference note`.

Keep project repository or workspace commits separate from memory repository commits.

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

`link` is idempotent and appends the note reference to `index.typ`. Do not use it as a routine end-of-session step.

## Guardrails

- Do not write memory for trivial details that are obvious from the project materials.
- Do not store secrets, tokens, private credentials, or transient logs.
- Keep note content factual and project-specific.
- Preserve user operations, preferences, and project conventions when they will matter later.
- Prefer one durable note over many low-signal notes.
- Treat `Memory.md` as generated output; source of truth is the managed zk-lsp wiki under the registered memory source path.
