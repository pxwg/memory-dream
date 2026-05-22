# Repository Guidelines

## Commit Policy

- Use Conventional Commits for all commit messages.
- Keep commits atomic: each commit should contain one coherent logical change.
- Do not mix unrelated formatting, refactors, feature work, fixes, or generated output in the same commit.
- Prefer commit types such as `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `build`, and `ci`.
- Use a scope when it clarifies the affected area, for example `feat(api): add memory lookup`.

## Commit Examples

```text
feat: add initial memory model
fix(storage): handle missing database file
docs: document local setup
test(api): cover empty search results
chore: update development tooling
```
