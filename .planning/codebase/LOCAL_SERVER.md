# Local server subtree (`local-server/`)

**Analysis Date:** 2026-03-28  
**Scope:** `local-server/` at repository root (user-requested map focus)

## Purpose (inferred)

The path suggests an optional **local reverse-proxy or multi-app layout** (common pattern: `nginx/` in front, `apps/` for services). Nothing in the template’s documented flow (`README.md`, `CLAUDE.md`, `project-context.mdc`, GitHub Actions) references this directory.

## Current contents

**Path:** `local-server/`

```
local-server/
├── apps/     # empty (no files, no .gitkeep)
└── nginx/    # empty (no files, no .gitkeep)
```

Verified on disk: both subdirectories exist but contain **no configuration, Dockerfiles, or compose files**.

## Relationship to the template

| Aspect | Status |
|--------|--------|
| CI (`pr-checks.yml`, `build-publish.yml`) | No references to `local-server/` |
| Container build | Uses `Dockerfile.template` at repo root, not under `local-server/` |
| Documented local run | Python venv + Flask/Gunicorn; optional `docker-compose.template.yml` at root |
| Backend entry | `backend/app/main.py`, `Dockerfile.template` |

So `local-server/` is **disconnected** from the production-ready path the template describes.

## Git behavior

Git does **not** track empty directories. With only empty `apps/` and `nginx/`, **`local-server/` will not appear in `git status` or in clones** unless files are added (e.g. `nginx.conf`, `docker-compose.yml`, `.gitkeep`). It may still exist on a developer machine as a leftover scaffold.

## Recommendations for template maintainers

1. **If intentional:** Add minimal files and docs — e.g. `local-server/README.md` explaining how nginx fronts the API, plus sample configs under `nginx/` and app stubs under `apps/`, and link from root `README.md`.
2. **If accidental:** Remove the directory locally and ensure it is not reintroduced; or add `local-server/` to `.gitignore` only if the team standardizes on a local-only layout that should never be committed (usually better to delete or fully document instead of ignoring).
3. **For clones of the template:** Consumers should not rely on `local-server/` until it contains real artifacts and is documented.

---

*Focused map: `local-server/` — 2026-03-28*
