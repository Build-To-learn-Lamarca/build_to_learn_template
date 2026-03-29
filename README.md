# build-to-learn-template — Template para microsserviços e páginas web

Template production-ready com **Clean Architecture + DDD**: APIs Python (Flask), testes com pytest (Python) e Jest (JavaScript), persistência em SQLite (dev) com interface trocável para qualquer banco.

> **Princípio de separação de responsabilidades:** o projeto contém apenas
> código de aplicação. O `Dockerfile`, `.dockerignore` e `docker-compose.yml`
> **não estão no repositório** — eles são **construídos pelo processo de CI/CD**
> (workflows GitHub Actions) e pelo script de setup local.

---

## Características

| Categoria | Ferramentas |
|---|---|
| Arquitetura | Clean Architecture + DDD (domain, application, infrastructure) |
| Framework | Flask 3 + Gunicorn |
| Banco (dev) | SQLite; porta trocável para PostgreSQL/outros |
| Qualidade de código | Black, isort, Ruff, mypy, pre-commit |
| Testes Python | pytest + pytest-cov (unit + integration) |
| Testes JavaScript | Jest (ex.: `scripts/js/`, frontend futuro) |
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
│   │   ├── __init__.py              # Application factory + wiring (create_app)
│   │   ├── main.py                  # Entry point (gunicorn)
│   │   ├── config.py                # Config (LOG_LEVEL, SQLITE_PATH, DATABASE_URL)
│   │   ├── domain/                  # DDD — entidades e value objects
│   │   │   └── entities/
│   │   ├── application/             # Portas, use cases, DTOs
│   │   │   ├── ports/
│   │   │   ├── use_cases/
│   │   │   └── dto/
│   │   └── infrastructure/
│   │       ├── persistence/        # Repositórios (ex.: SQLite)
│   │       └── http/
│   │           ├── controllers/    # Chamam use cases, retornam (body, status)
│   │           └── routes/         # Blueprints: request → controller → response
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── unit/                    # domain, application, infrastructure
│   │   └── integration/
│   │       └── http/                # Testes de rotas (client)
│   ├── requirements.txt
│   └── requirements-dev.txt
├── scripts/
│   └── js/                          # Exemplo e testes Jest (npm test)
├── .github/
│   ├── workflows/
│   │   ├── pr-checks.yml
│   │   └── build-publish.yml
│   ├── dependabot.yml
│   ├── CODEOWNERS
│   └── PULL_REQUEST_TEMPLATE.md
├── .pre-commit-config.yaml
├── pyproject.toml
├── package.json                     # npm test (Jest)
├── jest.config.js
└── .env.example
```

> Não há `Dockerfile`, `docker-compose.yml` nem `.dockerignore` no projeto.
> Veja a seção **Rodar com Docker localmente** para gerar esses arquivos.

---

## Como adicionar um novo domínio/entidade

Seguindo Clean Architecture + DDD, para expor um novo recurso (ex.: `Product`) na API:

1. **Domain** — Crie a entidade em `backend/app/domain/entities/<nome>.py` (dataclass com id e atributos). Escreva testes em `backend/tests/unit/domain/entities/test_<nome>.py`.

2. **Application — Porta** — Defina a interface do repositório em `backend/app/application/ports/<nome>_repository.py` (Protocol com `list()`, `add()`, etc.). Exporte em `application/ports/__init__.py`.

3. **Application — DTOs** — Crie request/response em `backend/app/application/dto/<nome>_dto.py` (ex.: `CreateProductRequest`, `ProductResponse.from_entity()`). Exporte em `application/dto/__init__.py`.

4. **Application — Use cases** — Implemente os casos de uso em `backend/app/application/use_cases/<nome>.py` (ex.: `ListProductsUseCase`, `CreateProductUseCase`) injetando a porta do repositório. Teste com um fake em `backend/tests/unit/application/use_cases/`.

5. **Infrastructure — Persistência** — Implemente a porta em `backend/app/infrastructure/persistence/sqlite/<nome>_repository.py` (e adicione a tabela em `schema.py` e em `backend/migrations/001_initial.sql` ou em uma nova migration). Teste em `backend/tests/unit/infrastructure/persistence/`.

6. **Infrastructure — HTTP** — Crie o controller em `backend/app/infrastructure/http/controllers/<nome>_controller.py` e o blueprint em `backend/app/infrastructure/http/routes/<nome>.py` (factory que recebe controller e limiter). Registre o blueprint em `create_app()` em `backend/app/__init__.py` (repositório → use cases → controller → blueprint). Adicione testes de integração em `backend/tests/integration/http/test_<nome>.py`.

---

## Usando este template

### 1. Criar repositório a partir do template

1. Clique em **Use this template** → **Create a new repository**.
2. Escolha o nome do repositório — esse será o **nome do projeto** e também o
   nome da imagem publicada no Docker Hub
   (`DOCKERHUB_USERNAME/<nome-do-repo>`).

### 2. Configurar Docker Hub (build e publicação de imagens)

O CI/CD publica a imagem no Docker Hub em todo merge na `main`. É preciso configurar **uma vez** por repositório (ou na organização, para todos os repos).

#### 2.1 Conta no Docker Hub

- Crie uma conta em [hub.docker.com](https://hub.docker.com) ou use a da organização.
- O nome de usuário define o prefixo das imagens: `DOCKERHUB_USERNAME/<nome-do-repo>` (ex.: `minhaorg/build_to_learn_template`).

#### 2.2 Token de acesso (para o GitHub Actions)

1. No Docker Hub: **Account Settings** → **Security** → **New Access Token**.
2. Nome sugerido: `github-actions-<nome-do-repo>`.
3. Permissão: **Read, Write, Delete** (o workflow faz push da imagem).
4. Copie o token (ele só é exibido uma vez).

Como gerar: [Docker Hub → New Access Token](https://hub.docker.com/settings/security)

#### 2.3 Secrets e Variables no GitHub

No repositório (ou na organização): **Settings** → **Secrets and variables** → **Actions**:

| Tipo     | Nome                | Valor                          |
|----------|---------------------|--------------------------------|
| **Secret**   | `DOCKERHUB_TOKEN`   | Token gerado no passo 2.2 (build **e** deploy: `docker login` no runner) |
| **Variable** | `DOCKERHUB_USERNAME`| Usuário ou organização no Docker Hub |

- Em **Organization** → Settings → Secrets and variables → Actions: configurar aqui faz os repos herdarem (recomendado para vários projetos).
- Em **Repository** → Settings → Secrets and variables → Actions: configurar só neste repo.

#### 2.3.1 Runner self-hosted na VM (deploy)

O job **deploy** usa `runs-on: [self-hosted, deploy]` — não há SSH a partir do GitHub; o agente do Actions corre **na própria VM** onde a aplicação vai ser executada.

1. **Na VM (ex.: OCI, Ubuntu):** instalar [Docker Engine](https://docs.docker.com/engine/install/ubuntu/). O utilizador que executa o runner deve conseguir correr `docker` sem `sudo` após `sudo usermod -aG docker ubuntu` (ou `sudo usermod -aG docker "$USER"`) — **termina sessão e volta a entrar** (ou reinicia o serviço `actions.runner.*`) para o grupo `docker` aplicar; caso contrário o job `deploy` falha em `docker pull`.
2. **Registar o runner no GitHub:** repositório → **Settings** → **Actions** → **Runners** → **New self-hosted runner** → escolher **Linux** e seguir os comandos (download, `config.sh` com URL e token).
3. **Label obrigatório:** durante `./config.sh`, quando pedir labels, incluir **`deploy`** em lista separada por vírgulas (junto com `self-hosted`, conforme o assistente do GitHub mostrar). Exemplo conceitual: `self-hosted, deploy`. Sem o label `deploy`, o job de deploy não é atribuído a este runner.
4. **Serviço:** após testar com `./run.sh`, instalar como serviço a partir da pasta do runner: `sudo ./svc.sh install` e `sudo ./svc.sh start`.
5. **Firewall / OCI:** a VM precisa de **saída HTTPS** para `github.com` e para o Docker Hub; não é necessário abrir SSH ao GitHub (o runner inicia ligações de saída).

Se tiveres vários runners na org, o label `deploy` garante que só a máquina certa recebe o job de deploy.

#### 2.3.2 Nginx e TLS (HTTPS autoassinado no IP público)

O job `deploy` em `.github/workflows/build-publish.yml` sobe o contentor e faz smoke em **`http://127.0.0.1:5000/health`**. Para expor a API na Internet com **HTTPS** no **IPv4 público** (sem FQDN), usa **Nginx** na VM como reverse proxy para `http://127.0.0.1:5000` e um certificado **autoassinado** com **Subject Alternative Name** no IP.

1. **Instalar Nginx e OpenSSL (Ubuntu 22.04):**

   ```bash
   sudo apt-get update && sudo apt-get install -y nginx openssl
   ```

2. **Diretório de certificados (exemplo):**

   ```bash
   sudo mkdir -p /etc/nginx/ssl
   ```

   Coloca aqui `server.key` e `server.crt` (ou ajusta os caminhos no `server` block abaixo).

3. **Gerar certificado autoassinado com SAN no IP** — substitui **`PUBLIC_IP`** pelo IPv4 público da VM (mantém o texto como placeholder na documentação; na VM usa o valor real):

   ```bash
   sudo openssl req -x509 -nodes -newkey rsa:2048 -days 825 \
     -keyout /etc/nginx/ssl/server.key \
     -out /etc/nginx/ssl/server.crt \
     -subj "/CN=PUBLIC_IP" \
     -addext "subjectAltName=IP:PUBLIC_IP"
   ```

4. **Bloco `server` (esboço)** — `server_name` com o **mesmo** IP público; proxy para a app no host:

   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate     /etc/nginx/ssl/server.crt;
       ssl_certificate_key /etc/nginx/ssl/server.key;
       server_name PUBLIC_IP;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   - **HTTP (porta 80):** podes redirecionar tudo para HTTPS, por exemplo `return 301 https://$host$request_uri;` num `server { listen 80; ... }`. O browser vai avisar no certificado autoassinado até haver domínio e CA confiável (ex.: Let’s Encrypt).

5. **Recarregar Nginx:** `sudo nginx -t && sudo systemctl reload nginx`

#### 2.3.3 Firewall OCI / NSG e portas

**Ingresso TCP na VM:** **22** (SSH), **80** (HTTP, se usares redirect ou health), **443** (HTTPS). Configura **security lists** / **NSG** na OCI em conformidade; não abras portas extra sem necessidade.

**Saída:** HTTPS para `github.com` (runner) e para o Docker Hub (`docker pull`), conforme já necessário para o deploy.

#### 2.3.4 Smoke tests (HTTPS público)

- A partir da Internet (aceita certificado não confiável com **`-k`** / `--insecure`):

  ```bash
  curl -fsS -k "https://PUBLIC_IP/health"
  ```

- Modo verboso para depuração TLS:

  ```bash
  curl -vk "https://PUBLIC_IP/health"
  ```

- Na própria VM, forçando o nome/IP a resolver para loopback (útil para testar SNI/cert sem sair da máquina):

  ```bash
  curl -fsS -k "https://127.0.0.1/health" --resolve "PUBLIC_IP:443:127.0.0.1"
  ```

O **`-k`** é **esperado** enquanto o certificado não for emitido por uma CA confiável. O workflow de CI já valida o contentor em **HTTP** em `127.0.0.1:5000`; a verificação **pública** é via **Nginx na porta 443**. Detalhes do job: `.github/workflows/build-publish.yml`.

#### 2.4 Uso local (Docker CLI / Docker Desktop)

Para fazer `docker pull` ou `docker push` no seu ambiente (fora do GitHub Actions):

```bash
docker login
# Username: seu-usuario-dockerhub
# Password: use o token (não a senha da conta) se a conta tiver 2FA
```

Depois do login, você pode puxar a imagem publicada pelo CI, por exemplo:

```bash
docker pull DOCKERHUB_USERNAME/build_to_learn_template:latest
```

#### 2.5 Segurança de credenciais no CI/CD

Para evitar vazamento de credenciais:

- **Token:** use apenas **Secret** (`DOCKERHUB_TOKEN`). O workflow usa somente o passo **Login to Docker Hub** (action `docker/login-action`), que não faz echo nem log do valor — o GitHub mascara automaticamente secrets que apareçam em logs.
- **Username:** use **Variable** (`DOCKERHUB_USERNAME`); não é sensível e pode aparecer em env e no Summary do job.
- **Deploy (runner self-hosted):** o token do Docker Hub é usado só no passo **Login to Docker Hub** (`docker/login-action`) no job que corre no runner; não uses `echo` de secrets em scripts.
- **Nunca:** fazer `echo`, `print` ou passar secrets para scripts nos workflows. Nenhum artefato enviado pelo CI deve conter `.env` ou tokens (o job **Check no .env committed** em PRs bloqueia commit de `.env`/`*.env`).

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

Principais variáveis (ver `.env.example`):

| Variável | Uso |
|----------|-----|
| `LOG_LEVEL` | Nível de log (DEBUG, INFO, etc.) |
| `DEBUG` | Modo debug Flask (nunca `true` em produção) |
| `SECRET_KEY` | Chave secreta Flask |
| `SQLITE_PATH` | Caminho do arquivo SQLite em dev (padrão: `data/app.db`) |
| `DATABASE_URL` | Em produção, definir para outro banco (ex.: PostgreSQL) |

### Rodar testes

```bash
# Testes Python (pytest) — unit + integration
cd backend  # ou, a partir da raiz:
python -m pytest backend/tests/ -v

# Com cobertura
python -m pytest backend/tests/ --cov=app --cov-report=term-missing

# Testes JavaScript (Jest) — quando houver código em scripts/js ou frontend
npm install
npm test
```

### Rodar localmente

```bash
# A partir da raiz do repositório (backend no PYTHONPATH)
cd backend
python -m app.main

# Ou com gunicorn (a partir da raiz, com backend no path)
cd backend && gunicorn --bind 0.0.0.0:5000 --reload app.main:app
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
    ├── Push → Docker Hub (latest + sha-<commit>)
    └── deploy → runner **self-hosted** na VM (label `deploy`), `docker pull`, reinício do contentor, smoke `curl` em `/health`

**`paths-ignore` no `push` para `main`:** alterações que tocam **apenas** `*.md` ou `docs/**` **não** disparam o workflow — não há build, push nem deploy. Para publicar imagem e deploy, o merge precisa incluir pelo menos um ficheiro fora desses caminhos.

---

### Produção na VM (variáveis de ambiente)

A imagem publicada pelo CI **não** inclui `SECRET_KEY` nem outros segredos. Na VM, passa variáveis em tempo de execução, por exemplo:

```bash
docker run -d --name "<app>" ... --env-file /path/to/app.env ...
```

O ficheiro `app.env` deve existir **só na VM**, permissões restritas (ex.: `chmod 600`), e **nunca** ser commitado.

**Mínimo recomendado em produção:** `SECRET_KEY` (obrigatório), `DEBUG=false`, opcionalmente `LOG_LEVEL` — os nomes alinham com `.env.example` na raiz do repositório.

**Follow-up (opcional, hardening):** o job `deploy` em `.github/workflows/build-publish.yml` usa hoje `-p 5000:5000`, o que publica a porta em todas as interfaces. Depois de validares Nginx em **443** como única entrada pública (D-04), podes alterar para `-p 127.0.0.1:5000:5000` no workflow para o contentor só escutar em loopback — **não** é obrigatório nesta fase; trata-se de melhoria de defesa em profundidade documentada para um PR futuro.

**Nota:** o deploy assume Docker na VM e porta **5000** no contentor; o nome do contentor segue o repositório. Não coloques segredos no YAML do GitHub Actions.

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
