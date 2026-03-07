# api-container — Template de API Containerizada

Template production-ready para APIs Python (Flask) containerizadas com CI/CD
automatizado no GitHub Actions.

> **Princípio de separação de responsabilidades:** o projeto contém apenas
> código de aplicação. O `Dockerfile`, `.dockerignore` e `docker-compose.yml`
> **não estão no repositório** — eles são **construídos pelo processo de CI/CD**
> (workflows GitHub Actions) e pelo script de setup local. Isso mantém o projeto
> limpo de infraestrutura e centraliza a definição da imagem no CI/CD.

---

## Características

| Categoria | Ferramentas |
|---|---|
| Framework | Flask 3 + Gunicorn |
| Qualidade de código | Black, isort, Ruff, mypy, pre-commit |
| Testes | pytest + pytest-cov |
| Container | Docker multi-stage (non-root) — construído pelo CI/CD |
| CI — Lint & Test | GitHub Actions (Ruff, mypy, pytest) |
| CI — SAST | Bandit (Python) → SARIF → GitHub Code Scanning |
| CI — DAST | OWASP ZAP Baseline Scan (imagem construída no workflow) |
| CD | Trivy image scan → Docker Hub (imagem construída no workflow) |
| Segurança contínua | Dependabot (pip + Actions), Secret Scanning |
| Branch policy | PR obrigatória, Code Owner review, push direto bloqueado |

---

## Estrutura do repositório

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Application factory
│   │   ├── main.py              # Entry point (gunicorn)
│   │   └── routes/
│   │       ├── health.py        # GET /health, GET /ready
│   │       └── example.py       # GET /api/v1/items, POST /api/v1/items
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_health.py
│   │   └── test_example.py
│   ├── requirements.txt
│   └── requirements-dev.txt
├── .github/
│   ├── workflows/
│   │   ├── pr-checks.yml        # Lint + SAST + DAST na PR (constrói Dockerfile inline)
│   │   └── build-publish.yml    # Constrói Dockerfile → Trivy scan → Docker Hub
│   ├── dependabot.yml
│   ├── CODEOWNERS
│   └── PULL_REQUEST_TEMPLATE.md
├── .pre-commit-config.yaml
├── pyproject.toml               # Black, isort, Ruff, mypy, pytest config
└── .env.example
```

> Não há `Dockerfile`, `docker-compose.yml` nem `.dockerignore` no projeto.
> Veja a seção **Rodar com Docker localmente** para gerar esses arquivos.

---

## Usando este template

### 1. Criar repositório a partir do template

1. Clique em **Use this template** → **Create a new repository**.
2. Escolha o nome do repositório — esse será o **nome do projeto** e também o
   nome da imagem publicada no Docker Hub
   (`DOCKERHUB_USERNAME/<nome-do-repo>`).

### 2. Configurar Secrets e Variables no GitHub

Em **Settings → Secrets and variables → Actions**:

| Tipo | Nome | Valor |
|---|---|---|
| Secret | `DOCKERHUB_TOKEN` | Token de acesso do Docker Hub (read+write) |
| Variable | `DOCKERHUB_USERNAME` | Seu usuário no Docker Hub |

Como gerar o token Docker Hub: [Docker Hub → Account Settings → Security → New Access Token](https://hub.docker.com/settings/security)

### 3. Configurar CODEOWNERS

Edite `.github/CODEOWNERS` e substitua os placeholders pelos usuários/teams reais:

```
*   @sua-org/seu-time
```

### 4. Criar a branch `homolog` e habilitar branch protection

**Branch `homolog` (homologação):** o fluxo usa três níveis — feature → homolog → main. A branch `homolog` deve existir. Crie-a uma vez a partir de `main`:

```bash
git checkout main && git pull origin main
git checkout -b homolog && git push -u origin homolog
```

**Proteção da branch `main` (produção):**

- Require a pull request before merging
- Require review from Code Owners (apenas o time CODEOWNERS aprova merge em main)
- Require status checks: `check-env`, `lint-test`, `sast`, `dast`
- Do not allow bypassing
- Convenção: merge em `main` apenas a partir de `homolog` (PR homolog → main)

**Proteção da branch `homolog` (testes):**

- Require a pull request before merging
- Require status checks: `check-env`, `lint-test`, `sast`, `dast`
- Opcional: require 1 approval ou Code Owners review (conforme política do time)
- Do not allow bypassing

### 5. Habilitar Secret Scanning e Push Protection

Siga as instruções em [`templates/ci-cd/secret-scanning.md`](../../ci-cd/secret-scanning.md).

### 6. Configurar Dependabot

O arquivo `.github/dependabot.yml` já está pré-configurado. Para ativar os
alertas de segurança:

**Settings → Security → Dependabot alerts → Enable**

---

## Desenvolvimento local

### Pré-requisitos

- Python 3.11+
- Docker + Docker Compose
- `pre-commit` instalado

### Configurar ambiente

```bash
# Clonar (main = produção atual) e entrar na pasta
git clone https://github.com/<owner>/<repo>.git && cd <repo>

# Para implementar uma feature: criar branch a partir de main (ou homolog atualizado)
# e abrir PR para homolog — nunca PR direto para main para features.
git checkout main
git pull origin main
git checkout -b feature/minha-feature

# Criar virtualenv e instalar dependências de desenvolvimento
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\Activate.ps1       # Windows PowerShell

pip install -r backend/requirements-dev.txt

# Instalar hooks de pre-commit
pre-commit install
```

### Variáveis de ambiente

```bash
cp .env.example .env
# Editar .env com os valores locais (nunca commitar o .env)
```

### Rodar localmente

```bash
# Direto com Python (desenvolvimento)
python -m backend.app.main

# Ou com gunicorn
gunicorn --bind 0.0.0.0:5000 --reload backend.app.main:app
```

### Rodar com Docker localmente

O projeto não contém `Dockerfile` nem `docker-compose.yml` — esses arquivos são
construídos pelo CI/CD. Para rodar localmente, use o script de setup que
espelha exatamente o que o workflow faz:

```bash
# A partir da raiz do projeto
bash ../../templates/ci-cd/scripts/docker-setup.sh

# Ou, se estiver num repo standalone (fora do sandbox):
# Baixe o script de setup do template ci-cd e execute:
#   bash docker-setup.sh

docker compose up --build
# API disponível em: http://localhost:5000
```

O script gera `Dockerfile`, `.dockerignore` e `docker-compose.yml` no diretório
atual. Adicione esses arquivos ao `.gitignore` do projeto — eles pertencem ao
CI/CD, não ao código:

```bash
echo "Dockerfile" >> .gitignore
echo ".dockerignore" >> .gitignore
echo "docker-compose.yml" >> .gitignore
```

### Testar

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=backend/app --cov-report=term-missing

# Endpoints manualmente
curl http://localhost:5000/health
curl http://localhost:5000/ready
curl http://localhost:5000/api/v1/items
curl -X POST http://localhost:5000/api/v1/items \
     -H "Content-Type: application/json" \
     -d '{"name": "Widget"}'
```

### Lint e formatação manual

```bash
# Executar todos os hooks
pre-commit run --all-files

# Individualmente
black backend/
isort backend/
ruff check backend/
mypy --config-file pyproject.toml
```

---

## Fluxo de CI/CD

Fluxo em três níveis: **feature** → **homolog** (testes) → **main** (produção).

```
Commit local (branch de feature)
    │
    ▼
pre-commit  ── Black, isort, Ruff, mypy (bloqueia localmente)
    │
    ▼
Pull Request → homolog
    │
    ├── lint-test  ── Ruff, mypy, pytest (cobertura ≥ 80%)
    ├── sast       ── Bandit → SARIF → GitHub Code Scanning
    └── dast       ── Build + OWASP ZAP Baseline Scan
    │
    ▼
Merge em homolog (quando tudo estiver ok)
    │
    ▼
[Quando estável]  Pull Request homolog → main
    │
    ▼
Code Owner Review  ── Aprovação obrigatória (time CODEOWNERS)
    │
    ▼
Merge em main (produção)
    │
    ▼
build-publish
    ├── Build Docker image
    ├── Trivy scan (bloqueia se CRITICAL/HIGH)
    └── Push → Docker Hub (latest + sha-<commit>)
```

---

## Adicionando funcionalidades

### Banco de dados

1. Adicionar driver na `requirements.txt` (ex.: `psycopg2-binary` para PostgreSQL).
2. Descomentar o serviço `db` no `docker-compose.yml`.
3. Adicionar `DATABASE_URL` no `.env.example`.
4. Criar módulo `backend/app/db.py` com a lógica de conexão.

### Novos endpoints

1. Criar blueprint em `backend/app/routes/<resource>.py`.
2. Registrar o blueprint em `backend/app/__init__.py`.
3. Adicionar testes em `backend/tests/test_<resource>.py`.

---

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `LOG_LEVEL` | `INFO` | Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `DEBUG` | `false` | Ativa modo debug do Flask (nunca `true` em produção) |
| `SECRET_KEY` | — | Chave secreta Flask (obrigatória em produção) |
| `DATABASE_URL` | — | URL de conexão com banco (opcional) |
