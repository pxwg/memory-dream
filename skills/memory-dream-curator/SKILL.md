---
name: memory-dream-curator
description: Consolidate and curate Memory Dream project memory for any project type. Trigger when Codex should do a daily or periodic memory review, summarize recent work into durable decision or experience notes, preserve user operations or preferences, link valuable notes into Memory.md, remove duplication, rebuild artifacts, or verify project memory quality using the memory-dream CLI.
---

# Memory Dream Curator

Use this skill for periodic memory consolidation, not normal project work. The goal is to keep `Memory.md` useful as the project-level entry point while preserving detailed notes as linked cards.

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
- Keep reusable workflow, tool, debugging, integration, creative, research, or physical-process experiences.
- Merge or update notes that repeat the same lesson.
- Leave generated artifacts untouched.
- Avoid turning every task event into memory.

Use `memory-dream edit <id>` to locate source notes that need revision.

## Maintain The Entry Point

`index.typ` compiles to `Memory.md`, so it must be more than a flat ID list. During curation, make sure the generated `Memory.md` has:

- a compact Operational Contract near the top
- a short project-level overview that orients a future agent before any note is opened
- a small set of important entry links, not every note
- section labels or short prose that explain why linked notes matter
- lightweight links into major decision or experience clusters

Use this model:

```text
Memory.md = agent bootloader
memory/*.md = generated durable priors
note/*.typ = semantic source graph
zk-lsp = mutation interface
curator = consolidation/refactoring process
```

The Operational Contract should be short imperative bullets. Prefer this shape:

```typst
== Operational Contract

- Treat `note/*.typ` and `zk-lsp` as the formal source of truth.
- Treat generated Markdown artifacts as read-only consumption output.
- Prefer `zk-lsp` and `memory-dream` commands over ad-hoc file edits.
- Follow linked memory entries before expanding into source notes.
- Preserve semantic links, lifecycle metadata, and user-authored metadata.
- Promote only durable project knowledge into memory.
```

Prefer semantic navigation over direct disclosure. The first context load should explain the project memory shape and expose only high-value entry cards; detailed notes should be reached through card-to-card links.

Use `memory-dream open` to locate the source wiki and edit `index.typ` when the overview or entry structure needs changes. Then run `memory-dream build`.

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

Prefer `decision` for durable project choices and `experience` for lessons learned from work sessions, user operations, tools, process, or implementation.

Only link notes that are useful entry points. Do not link every active note directly from `index.typ`.

## Graph Hygiene

Run:

```bash
memory-dream check
```

Resolve orphan notes before finishing curation. For each orphan:

- link it from a relevant card if it is still active but too detailed for `index.typ`
- link it from `index.typ` only if it is an important entry point
- merge it into another note when it duplicates an existing memory
- archive or retire it in source metadata/content if it is no longer active

The goal is not maximum exposure. The goal is a navigable graph where active notes have semantic paths and `Memory.md` stays compact.

## Git Audit Trail

The managed source wiki is a git repository. Curator work must be auditable.

Commit each coherent consolidation as an atomic commit in the source wiki:

```bash
git status --short
git add index.typ note
git commit -m "docs(memory): curate project entry points"
```

Use Conventional Commits. Do not mix unrelated memory refactors, lifecycle changes, and new summaries in the same commit when they can be separated cleanly.

## Verification

After curating:

1. Run `memory-dream status --format json`.
2. Confirm `built` is true and `stale` is false.
3. Run `memory-dream check`.
4. Run `memory-dream context`.
5. Check that the default context contains an Operational Contract, a useful overview, the intended entry links, and no unnecessary note dump.

If `context` is too large or noisy, unlinking is not currently a CLI operation. Use `memory-dream open` to locate the source wiki, edit `index.typ` only when necessary, then run `memory-dream build`.

## Output

Report:

- notes created
- notes edited
- notes linked into Memory.md
- index overview or structure changes
- orphan notes resolved or intentionally archived
- build/context verification result
- any remaining unlinked notes worth future review

## Guardrails

- Do not edit `artifact/Memory.md` or files under `artifact/memory/`.
- Do not invent memories not supported by project context.
- Do not store secrets or transient logs.
- Keep summaries concise, factual, and reusable by future agents.
