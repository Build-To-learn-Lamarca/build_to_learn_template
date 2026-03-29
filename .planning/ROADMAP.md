# Roadmap: build_to_learn_template

**Created:** 2026-03-29
**Granularity:** coarse (3 phases)
**Source:** `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/codebase/*`

## Overview

| # | Phase | Goal | Requirements | Success criteria |
|---|-------|------|----------------|------------------|
| 1 | Template API baseline | API de exemplo + health/ready + deploy pós-merge (OCI VM) | API-01–API-04, D-01–D-07 | 4 |
| 2 | VM baseline (OCI) | Baseline OCI: runner com label `deploy`, deploy via `build-publish.yml`, Nginx + HTTPS autoassinado no **IP público**, smoke tests documentados. **ARCH-01 / QUAL-01–QUAL-03** adiados à fase/milestone seguinte (D-09). | VM-DEPLOY (D-01–D-05, D-09–D-12) | 3 |
| 3 | CI/CD alignment | Documentação e política de release alinhadas ao CI | CI-01, CI-02 | 2 |

---

## Phase 1: Template API baseline

**Goal:** Manter `items` + health/ready como contrato mínimo do template; qualquer regressão é inaceitável. Incluir CD pós-merge: após push da imagem no Docker Hub (`main`), deploy automático para VM OCI (SSH) conforme `01-CONTEXT.md` (D-01..D-07).

**Canonical refs:**

- `README.md` — visão e estrutura
- `.planning/codebase/ARCHITECTURE.md` — fluxo HTTP → use case → repositório
- `backend/app/infrastructure/http/routes/health.py`, `.../items.py`
- `.github/workflows/build-publish.yml` — build → Trivy → push → deploy

**Requirements:** API-01, API-02, API-03, API-04, D-01..D-07 (decisões de deploy em `01-CONTEXT.md`)

**Plans:** 2 plans

Plans:

- [ ] `01-PLAN.md` — Verificar integração API-01..API-04 (pytest + rastreio); opcional alinhar texto da Fase 1 no ROADMAP com CONTEXT
- [ ] `02-PLAN.md` — Job `deploy` (`appleboy/ssh-action`, `needs: build-scan-push`) + README (secrets SSH, segurança, paths-ignore)

**Success criteria:**

1. Documentação do README descreve as rotas de exemplo, o fluxo CI/CD (incluindo deploy) e está alinhada ao código e workflows.
2. Testes de integração cobrem health, ready e items (happy path mínimo).
3. Nenhuma mudança quebra o contrato JSON documentado sem atualizar README/tests.
4. Workflow de release publica imagem e, em seguida, executa deploy por SSH sem expor credenciais no repositório.

**UI hint:** no

---

## Phase 2: VM baseline — OCI (runner, Docker, Nginx, HTTPS)

**Goal:** Entregar o baseline de `02-CONTEXT.md`: runner self-hosted na mesma VM (D-01), aplicação em contentor, Nginx como **único** ponto de entrada HTTP(S) público (D-04), HTTPS com certificado **autoassinado** incluindo **IP SAN** (D-05), smoke tests documentados. **Esta fase não implementa** ARCH-01 nem QUAL-01–QUAL-03 no repositório (D-09); esse trabalho fica para **milestone / fase seguinte** (ver secção **Deferred / backlog** no fim deste ficheiro).

**Canonical refs:**

- `.planning/phases/02-quality-extensibility/02-CONTEXT.md`
- `README.md` — secção operador VM / Nginx / smoke
- `.github/workflows/build-publish.yml` — job `deploy` (`runs-on: [self-hosted, deploy]`)

**Requirements:** `VM-DEPLOY`; decisões D-01–D-05, D-09–D-12 em `02-CONTEXT.md`.

**Plans:** 3 plans

Plans:

- [ ] `02-01-PLAN.md` — ROADMAP Phase 2 aligned to VM baseline + D-09
- [ ] `02-02-PLAN.md` — README: runner, Docker, Nginx, OpenSSL IP SAN, OCI ports, HTTPS smoke
- [ ] `02-03-PLAN.md` — Production env docs (SECRET_KEY / .env.example) + optional localhost bind follow-up

**Deferred / backlog (esta fase):**

- `ARCH-01, QUAL-01–QUAL-03` (guia de qualidade / extensão do template): agendado **após** a fase baseline VM, conforme **D-09**.

**Success criteria:**

1. ROADMAP documenta âmbito VM e adiamento explícito de ARCH/QUAL (D-09); referência a `02-02-PLAN.md` na lista de plans.
2. README descreve runner com label `deploy`, `svc.sh`, grupo `docker`, Nginx com ficheiros em `/etc/nginx/ssl/` (ou equivalente), `proxy_pass http://127.0.0.1:5000;`, OpenSSL com SAN `IP:PUBLIC_IP`, ingress OCI **22**, **80**, **443**, smoke `curl -fsS -k https://PUBLIC_IP/health`.
3. Nenhum segredo no repositório; variáveis de produção documentadas sem valores reais.

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

- **ARCH-01, QUAL-01–QUAL-03** (guia de qualidade / extensão do template no repo): **após** baseline VM — **D-09**; não fazem parte da entrega da Fase 2 atual.
- Pesquisa de domínio em `.planning/research/` — opcional; executar `/gsd-plan-phase` com research se necessário.
- Múltiplas VMs / regiões / ambientes (staging/prod separados) — fora da Fase 1; a Fase 1 fixa um único alvo OCI conforme `01-CONTEXT.md` (D-03).

---

*Roadmap: build_to_learn_template — 2026-03-29*
