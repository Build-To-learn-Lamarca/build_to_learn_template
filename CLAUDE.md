# CLAUDE.md — Template build-to-learn

Documento de contexto para agentes e desenvolvedores. Repositório base: **Build-To-learn-Lamarca/build_to_learn_template**.

---

## 1. Visão geral da arquitetura

- **Objetivo:** Template production-ready para microsserviços e páginas web em Python (Flask), com Clean Architecture + DDD, testes (pytest + Jest), SQLite em dev e persistência trocável.
- **Tipo:** API REST (Flask); pronto para adicionar workers ou gateways.
- **Repositório:** `https://github.com/Build-To-learn-Lamarca/build_to_learn_template`
- **Dependências externas:** Nenhuma obrigatória; opcional PostgreSQL via `DATABASE_URL`.
- **Porta padrão:** 5000

Fluxo de dependência: **infrastructure → application → domain** (domínio sem dependências externas).

- **Domain:** entidades e value objects (sem Flask/DB).
- **Application:** portas (interfaces de repositório), use cases por domínio (`use_cases/items/`), DTOs.
- **Infrastructure:** persistência (SQLite, migrações em `backend/migrations/`), HTTP (controllers, rotas, error handlers, rate limiting).

---

## 2. Stack tecnológico completo

| Camada | Tecnologia | Versão / nota |
|--------|------------|----------------|
| Runtime | Python | 3.11+ |
| Framework | Flask | 3.0.x |
| Servidor WSGI | Gunicorn | 22.x |
| Logging | structlog | 24.x — JSON em prod, console em dev |
| Rate limiting | flask-limiter | 3.5.x — items blueprint (60/30 por minuto) |
| Testes (Python) | pytest, pytest-cov | 8.x |
| Testes (JavaScript) | Jest | 29.x |
| Linter | Ruff | 0.5.x |
| Formatter | Black | 24.x |
| Import sorter | isort | 5.x |
| Type checker | mypy | 1.x |
| Pre-commit | pre-commit | — |
| Container | Docker (multi-stage, non-root) | Construído pelo CI/CD |
| CI/CD | GitHub Actions | pr-checks, build-publish |
| SAST | Bandit | 1.7.x |
| DAST | OWASP ZAP Baseline | — |
| Image scan | Trivy | — |
| Registry | Docker Hub | — |
| Dependências | Dependabot (pip + Actions) | — |
| Banco (dev) | SQLite (stdlib) | `SQLITE_PATH`, `:memory:` em testes |
| Banco (prod) | Configurável | `DATABASE_URL` (ex.: PostgreSQL) |
| Migrações | SQL script + opcional Alembic | `backend/migrations/` |

---

## 3. Estrutura do diretório

```
build_to_learn_template/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # create_app: config, logging, DB, limiter, blueprints
│   │   ├── main.py                  # Entry point gunicorn
│   │   ├── config.py                # get_config() — env
│   │   ├── logging_config.py       # structlog (JSON/console)
│   │   ├── domain/
│   │   │   ├── entities/            # ex.: item.py
│   │   │   └── value_objects/
│   │   ├── application/
│   │   │   ├── ports/               # ex.: item_repository.py (Protocol)
│   │   │   ├── use_cases/           # por domínio: items/create_item.py, list_items.py
│   │   │   └── dto/
│   │   └── infrastructure/
│   │       ├── persistence/
│   │       │   └── sqlite/          # schema, item_repository
│   │       └── http/
│   │           ├── error_handlers.py # 400, 404, 405, 429, 500 JSON
│   │           ├── controllers/
│   │           └── routes/          # health, items (com limiter)
│   ├── migrations/
│   │   ├── 001_initial.sql          # Schema SQLite (fora de :memory:)
│   │   └── README.md                # Como rodar / Alembic
│   ├── tests/
│   │   ├── conftest.py              # app, client, path backend
│   │   ├── unit/                    # domain, application, infrastructure
│   │   └── integration/
│   │       └── http/                # health, items, error_handlers
│   ├── requirements.txt
│   └── requirements-dev.txt
├── scripts/
│   └── js/                          # Exemplo + testes Jest
├── .github/
│   ├── workflows/                   # pr-checks.yml, build-publish.yml
│   ├── dependabot.yml
│   ├── CODEOWNERS
│   └── PULL_REQUEST_TEMPLATE.md
├── .cursor/rules/
│   └── project-context.mdc
├── .pre-commit-config.yaml
├── pyproject.toml
├── package.json
├── jest.config.js
├── .env.example
├── CLAUDE.md                        # Este arquivo
└── README.md
```

---

## 4. Serviços, jobs e models

### Endpoints da API

| Método | Path | Descrição | Auth | Rate limit |
|--------|------|-----------|------|------------|
| GET | `/health` | Liveness | Não | — |
| GET | `/ready` | Readiness | Não | — |
| GET | `/api/v1/items` | Listar itens | Não | 60/min |
| POST | `/api/v1/items` | Criar item (`{"name": "string"}`) | Não | 30/min |

### Respostas de erro (JSON padronizado)

- 400: `{"error": "Bad Request", "code": "BAD_REQUEST"}`
- 404: `{"error": "Not Found", "code": "NOT_FOUND"}`
- 405: `{"error": "Method Not Allowed", "code": "METHOD_NOT_ALLOWED"}`
- 429: `{"error": "Too Many Requests", "code": "RATE_LIMIT_EXCEEDED"}`
- 500: `{"error": "Internal Server Error", "code": "INTERNAL_ERROR"}`

### Jobs / Workers

Nenhum no template; adicionar em projetos derivados.

### Entidades de domínio

| Model | Campos | Persistência |
|-------|--------|--------------|
| Item | id, name | SQLite (dev); porta `ItemRepository` trocável |

### Portas (application/ports)

| Porta | Descrição |
|-------|-----------|
| ItemRepository | `list() -> list[Item]`, `add(item: Item) -> Item` |

---

## 5. Common hurdles e soluções documentadas

| Problema | Causa provável | Solução |
|----------|----------------|---------|
| pre-commit falha "mypy not found" | mypy não no venv | `pip install -r backend/requirements-dev.txt` |
| Black e isort em conflito | isort sem `profile = "black"` | `[tool.isort] profile = "black"` no pyproject.toml |
| Trivy bloqueia build por CVE | Vuln em dependência | Atualizar pacote ou `ignore-unfixed: true` |
| ZAP DAST timeout | App não sobe a tempo no CI | Aumentar iterações do wait no job dast (pr-checks.yml) |
| DOCKERHUB_TOKEN não encontrado | Secret não herdado da org | Settings → Secrets → org secret visível |
| Rate limiter "weakly-referenced object" | Limiter GC’d antes das rotas | Manter `app.extensions["limiter"] = limiter` em create_app |
| Branch protection bloqueia push | Política correta | PR para homolog/main; não push direto em main |
| PR aberta para main (feature) | Fluxo é feature → homolog → main | Fechar e abrir PR para `homolog` |
| Push rejeitado "without workflow scope" | Token gh sem permissão | `gh auth refresh -h github.com -s workflow` |
| Push "Changes must be made through a PR" | Branch protection | Fazer PR; merge com bypass ou desproteger temporariamente |

---

## 6. Design patterns do template

- **Clean Architecture + DDD:** domain → application (portas, use cases, DTOs) → infrastructure (persistência, HTTP).
- **Application factory:** `create_app()` em `backend/app/__init__.py` — wiring manual (config, logging, DB, limiter, error handlers, blueprints).
- **Controllers vs rotas:** rotas só parseiam request e chamam controller; controllers recebem DTOs, chamam use cases, retornam (body, status).
- **Portas e adapters:** portas em `application/ports/`; implementações em `infrastructure/persistence/` (ex.: SQLite); trocar DB sem mudar domínio/aplicação.
- **Use cases por domínio:** `application/use_cases/items/` (create_item, list_items); re-export em `application/use_cases/__init__.py`.
- **Error handlers globais:** `register_error_handlers(app)` — 400, 404, 405, 429, 500 em JSON.
- **Logging:** structlog; JSON quando `LOG_FORMAT=json` ou `DEBUG=false`; console em dev.
- **Rate limiting:** flask-limiter no blueprint de items; desligado quando `TESTING=true`.
- **Migrações:** SQL em `backend/migrations/`; opcional Alembic para PostgreSQL.
- **Testes:** pytest (unit + integration); Jest para JS; failure paths (repositório levanta → use case propaga).
- **PR-first:** feature → homolog → main; code owner no merge para main.

---

## 7. Checklist pós-implementação

Após mudanças relevantes:

### Código

- [ ] Testes passando (`pytest backend/tests/`, `npm test`)
- [ ] `pre-commit run --all-files` OK (Black, isort, Ruff, mypy)
- [ ] Sem secrets no código; `.env.example` atualizado

### CI/CD

- [ ] PR para `homolog` (nunca direto para main)
- [ ] Jobs check-env, lint-test, sast, dast verdes
- [ ] Release: PR homolog → main com aprovação; build-publish e imagem no Docker Hub

### Documentação

- [ ] project-context.mdc e CLAUDE.md atualizados (endpoints, models, variáveis)
- [ ] README atualizado (rodar, testes, variáveis)
- [ ] Common hurdles atualizado se novo problema recorrente

### Segurança

- [ ] Sem alertas novos em Secret scanning
- [ ] Dependabot críticos/altos com plano
- [ ] Imagem sem CVEs críticos/altos (Trivy)
