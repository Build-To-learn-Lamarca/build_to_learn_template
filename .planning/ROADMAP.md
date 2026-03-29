# Roadmap: build_to_learn_template

**Created:** 2026-03-29
**Granularity:** coarse (3 phases)
**Source:** `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/codebase/*`

## Overview

| # | Phase | Goal | Requirements | Success criteria |
|---|-------|------|----------------|------------------|
| 1 | Template API baseline | Garantir API de exemplo e sondas como referência | API-01–API-04 | 4 |
| 2 | Quality & extensibility | Testes, lint, padrão de extensão de domínio | ARCH-01, QUAL-01–QUAL-03 | 4 |
| 3 | CI/CD alignment | Documentação e política de release alinhadas ao CI | CI-01, CI-02 | 2 |

---

## Phase 1: Template API baseline

**Goal:** Manter `items` + health/ready como contrato mínimo do template; qualquer regressão é inaceitável.

**Canonical refs:**

- `README.md` — visão e estrutura
- `.planning/codebase/ARCHITECTURE.md` — fluxo HTTP → use case → repositório
- `backend/app/infrastructure/http/routes/health.py`, `.../items.py`

**Requirements:** API-01, API-02, API-03, API-04

**Success criteria:**

1. Documentação do README descreve as rotas de exemplo e está alinhada ao código.
2. Testes de integração cobrem health, ready e items (happy path mínimo).
3. Nenhuma mudança quebra o contrato JSON documentado sem atualizar README/tests.

**UI hint:** no

---

## Phase 2: Quality & extensibility

**Goal:** Ferramentas de qualidade e guia “novo domínio” permanecem reproduzíveis e rastreados.

**Canonical refs:**

- `README.md` — seção “Como adicionar um novo domínio/entidade”
- `pyproject.toml`, `.pre-commit-config.yaml`
- `backend/tests/`, `scripts/js/`

**Requirements:** ARCH-01, QUAL-01, QUAL-02, QUAL-03

**Success criteria:**

1. Fluxo documentado no README continua aplicável (nomes de pastas/arquivos coerentes).
2. `pytest` e `npm test` documentados no README passam em ambiente limpo descrito.
3. Pre-commit pode ser executado conforme documentação do projeto.

**UI hint:** no

---

## Phase 3: CI/CD alignment

**Goal:** CI/CD e ausência de Dockerfile no repo permanecem decisões conscientes e documentadas.

**Canonical refs:**

- `.github/workflows/pr-checks.yml`, `.github/workflows/build-publish.yml`
- `README.md` — Docker Hub, branch policy

**Requirements:** CI-01, CI-02

**Success criteria:**

1. README menciona os jobs principais e variáveis esperadas sem divergir dos workflows.
2. Política “imagem construída no CI” explícita e sem contradição com o que está versionado.

**UI hint:** no

---

## Deferred / backlog

- Pesquisa de domínio em `.planning/research/` — opcional; executar `/gsd-plan-phase` com research se necessário.
- Deploy em VM cloud (ex.: OCI) — fora do núcleo do template; tratar em milestone ou notas operacionais.

---

*Roadmap: build_to_learn_template — 2026-03-29*
