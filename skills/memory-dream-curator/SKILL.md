---
name: memory-dream-curator
description: Consolidate and curate Memory Dream project memory. Trigger when Codex should do a daily or periodic memory review, summarize recent coding work into durable decision or experience notes, link valuable notes into Memory.md, remove duplication, rebuild artifacts, or verify project memory quality using the memory-dream CLI.
---

# Memory Dream Curator

Use this skill for periodic memory consolidation, not normal implementation. The goal is to keep `Memory.md` useful as the project-level entry point while preserving detailed notes as linked cards.

## Inputs

Use available local context first:

```bash
memory-dream status --format json
memory-dream list --format json
memory-dream context --all
```

If artifacts are stale or missing, run:

```bash
memory-dream build
```

Then rerun `memory-dream context --all`.

## Curate

Review notes for durable value:

- Keep project decisions, conventions, tradeoffs, and user preferences.
- Keep reusable debugging or integration experiences.
- Merge or update notes that repeat the same lesson.
- Leave generated artifacts untouched.
- Avoid turning every task event into memory.

Use `memory-dream edit <id>` to locate source notes that need revision.

## Promote Into Default Context

Important notes must be linked from the project entry point so they enter generated `Memory.md` and default `memory-dream context`.

Use:

```bash
memory-dream link <id> --build
```

For new durable summaries:

```bash
memory-dream new --title "<title>" --kind decision --content "<summary>" --link --build
memory-dream new --title "<title>" --kind experience --content "<summary>" --link --build
```

Prefer `decision` for durable project choices and `experience` for lessons learned from implementation or debugging.

## Verification

After curating:

1. Run `memory-dream status --format json`.
2. Confirm `built` is true and `stale` is false.
3. Run `memory-dream context`.
4. Check that the default context contains the intended Memory.md entry and linked notes.

If `context` is too large or noisy, unlinking is not currently a CLI operation. Use `memory-dream open` to locate the source wiki, edit `index.typ` only when necessary, then run `memory-dream build`.

## Output

Report:

- notes created
- notes edited
- notes linked into Memory.md
- build/context verification result
- any remaining unlinked notes worth future review

## Guardrails

- Do not edit `artifact/Memory.md` or files under `artifact/memory/`.
- Do not invent memories not supported by project context.
- Do not store secrets or transient logs.
- Keep summaries concise, factual, and reusable by future coding agents.
