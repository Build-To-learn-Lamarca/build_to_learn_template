# build_to_learn_template

## What This Is

Repositório **template** (Build-To-learn-Lamarca) para microsserviços e APIs web em **Python/Flask** com **Clean Architecture + DDD**: exemplo de domínio `Item`, persistência SQLite em desenvolvimento (porta trocável), testes **pytest** e **Jest**, CI/CD no GitHub Actions (sem Dockerfile no repo — imagem gerada no workflow).

Quem usa o template **forka**, define nome da imagem Docker Hub e estende domínios seguindo a seção “Como adicionar um novo domínio/entidade” do README.

## Core Value

Um esqueleto **production-ready** que qualquer time possa clonar e evoluir sem reescrever estrutura de pastas, testes ou pipeline — mantendo limites claros entre domínio, aplicação e infraestrutura.

## Requirements

### Validated

- ✓ API REST Flask com rotas de exemplo `items` (listar/criar) — existente
- ✓ Sondas `GET /health` e `GET /ready` — existente
- ✓ Persistência SQLite via porta `ItemRepository` + adapter — existente
- ✓ Camadas Clean Architecture (domain → application → infrastructure) — existente
- ✓ CI: `pr-checks.yml` (lint, testes, SAST, DAST) e `build-publish.yml` — existente
- ✓ Tooling: Black, isort, Ruff, mypy, pre-commit, pytest, Jest — existente
- ✓ Documentação operador VM (runner `deploy`, Nginx HTTPS IP SAN, smoke, `SECRET_KEY` / `.env.example`) — validado na Fase 2 (VM baseline)

### Active

- [ ] Manter roadmap GSD alinhado ao template e às prioridades do time
- [ ] Garantir que novos domínios sigam o padrão documentado no README sem quebrar contratos de CI

### Out of Scope

- **Dockerfile no repositório** — política do template; imagem é construída no CI (documentado no README)
- **UI completa** — template é API-first; front pode ser fase/milestone separado
- **Autenticação/OAuth na API de exemplo** — não faz parte do núcleo do template; adicionar em fork se necessário

## Context

- **Brownfield:** `.planning/codebase/` (STACK, ARCHITECTURE, etc.) descreve o estado atual.
- **Organização:** fluxo de branches e PRs descritos no README / CLAUDE.md.
- **Deploy:** referências operacionais (ex.: VM OCI) podem existir em notas/todos locais; não são pré-requisito do template em si.

## Constraints

- **Tech:** Python 3.11, Flask 3, SQLite em dev — compatível com `pyproject.toml` e CI
- **Cobertura:** pytest com `--cov-fail-under=80` no fluxo de qualidade esperado
- **Segurança:** não commitar `.env`; seguir `.env.example`

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Clean Architecture + DDD | Separação testável e troca de adapters | ✓ Good — mantido no código |
| Dockerfile apenas no CI | Repo contém só código de aplicação | ✓ Good — documentado |
| Inicialização GSD neste repo (`.`) | Formalizar `.planning/` para fases e rastreio | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):

1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):

1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---

*Last updated: 2026-03-29 — after Phase 2 (VM baseline documentation) execution*
