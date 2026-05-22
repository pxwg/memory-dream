# Memory Dream

Memory Dream is a local project-memory harness backed by [`zk-lsp`](https://github.com/pxwg/zk-lsp.typst).

It binds any real project directory to an isolated Typst Zettelkasten wiki under
`~/.memory-dream`, then builds that wiki into Markdown artifacts that agents can
consume.

`zk-lsp` is an intentional architectural dependency, not a temporary backend.
Memory Dream delegates ZK authoring, graph checks, note creation, metadata
semantics, and link management to `zk-lsp`; Memory Dream provides the project
binding, artifact build, context output, and agent workflow layer around it.

## Status

Early experimental `0.1.x`.

This project is useful for local trials and agent workflows, but it is not a
stable memory platform yet. The v1 design is intentionally bound to `zk-lsp`.

## Install

Requirements:

- Python 3.11+
- `uv`
- `zk-lsp` on `PATH`

Install the CLI from a checkout:

```bash
uv tool install --force --reinstall .
```

Verify:

```bash
memory-dream --help
zk-lsp --help
```

## Basic Flow

Register the current project:

```bash
memory-dream init
```

Build Markdown artifacts:

```bash
memory-dream build
```

Print AI-consumable context:

```bash
memory-dream context
```

Create ordinary project memory:

```bash
memory-dream new --title "Useful project lesson" --kind experience --content "..." --build
```

Promote an important entry note into `Memory.md`:

```bash
memory-dream link <id> --build
```

Inspect project memory state:

```bash
memory-dream status --format json
memory-dream list --format json
memory-dream check
```

## Model

```text
real project directory = the work object
~/.memory-dream        = the memory management root
source ZK wiki         = source of truth
Markdown artifact      = agent consumption output
```

The project directory does not need to contain memory files. Memory Dream stores
project bindings in `~/.memory-dream/dream.toml` and keeps each managed source
wiki under `~/.memory-dream/projects/<project-id>/source`.

Generated Markdown artifacts live under:

```text
~/.memory-dream/projects/<project-id>/artifact/
  Memory.md
  memory/
```

Do not edit generated artifacts. Edit the source wiki and rebuild.

## Agent Bootloader

`Memory.md` should behave as an agent bootloader, not a long README:

```text
Memory.md = agent bootloader
memory/*.md = generated durable priors
note/*.typ = semantic source graph
zk-lsp = mutation interface
curator = consolidation/refactoring process
```

The source `index.typ` should include a short Operational Contract, a concise
project overview, and a small set of high-value entry links. Detailed knowledge
belongs in source notes and card-to-card semantic links.

## Codex Skills

This repository includes three Codex skills:

```text
skills/memory-dream-project
skills/memory-dream-reader
skills/memory-dream-curator
```

Install them into a Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
rsync -a skills/memory-dream-project "${CODEX_HOME:-$HOME/.codex}/skills/"
rsync -a skills/memory-dream-reader "${CODEX_HOME:-$HOME/.codex}/skills/"
rsync -a skills/memory-dream-curator "${CODEX_HOME:-$HOME/.codex}/skills/"
```

`memory-dream-project` is for normal project sessions of any kind. It loads
project memory, keeps artifacts current, and records lightweight decisions,
experiences, user operations, or preferences.

`memory-dream-reader` is for read-only memory queries. It follows relevant
links and returns a compact task-specific memory bundle without editing memory.

`memory-dream-curator` is for periodic consolidation. It maintains the
`Memory.md` entry point, links durable entry memories, resolves or retires
orphan notes, rebuilds artifacts, and verifies context quality.

## Non-Goals

Memory Dream is not:

- a SQL database
- an embedding or vector search system
- a replacement for `zk-lsp`
- a provider-specific integration for one agent runtime
- a bidirectional sync tool from Markdown artifacts back to Typst source

## Development

Run tests:

```bash
uv run python -m unittest
uv run python -m compileall -q src tests
```

Build package artifacts:

```bash
uv build
```
