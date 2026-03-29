# Requirements: build_to_learn_template

**Defined:** 2026-03-29
**Core Value:** Template production-ready Flask + Clean Architecture que equipes podem clonar e estender sem reescrever base técnica.

## v1 Requirements

Escopo alinhado ao que o template já entrega e ao que o roadmap GSD vai manter explícito.

### API & probes

- [ ] **API-01**: `GET /health` responde com sucesso (liveness)
- [ ] **API-02**: `GET /ready` responde com sucesso (readiness)
- [ ] **API-03**: `GET /api/v1/items` lista itens em JSON
- [ ] **API-04**: `POST /api/v1/items` cria item com `name` válido e retorna representação consistente

### Arquitetura & extensão

- [ ] **ARCH-01**: Novo domínio segue o guia do README (entidade → porta → use case → SQLite → HTTP) sem quebrar limites de camada

### Qualidade

- [ ] **QUAL-01**: Testes Python (`pytest`) passam com cobertura mínima configurada no projeto
- [ ] **QUAL-02**: Pre-commit (Black, isort, Ruff, mypy conforme config) aplicável ao código Python alterado
- [ ] **QUAL-03**: Testes Jest em `scripts/js/` permanecem verdes quando JS mudar

### CI/CD & documentação

- [ ] **CI-01**: Workflows documentados no README permanecem coerentes com `.github/workflows/`
- [ ] **CI-02**: Política “sem Dockerfile no repo” mantida; geração no CI referenciada

## v2 Requirements

- **EXT-01**: Autenticação na API de exemplo — adicionar em fork ou milestone futuro
- **EXT-02**: Frontend de exemplo consumindo a API — fora do núcleo do template

## Out of Scope

| Feature | Reason |
|---------|--------|
| Dockerfile versionado no repositório | Decisão explícita do template; CI gera imagem |
| Multi-tenant / billing | Não é escopo do template base |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| API-01 | Phase 1 | Pending |
| API-02 | Phase 1 | Pending |
| API-03 | Phase 1 | Pending |
| API-04 | Phase 1 | Pending |
| ARCH-01 | Phase 2 | Pending |
| QUAL-01 | Phase 2 | Pending |
| QUAL-02 | Phase 2 | Pending |
| QUAL-03 | Phase 2 | Pending |
| CI-01 | Phase 3 | Pending |
| CI-02 | Phase 3 | Pending |

**Coverage:**

- v1 requirements: 10 total
- Mapped to phases: 10
- Unmapped: 0 ✓

---

*Requirements defined: 2026-03-29*
*Last updated: 2026-03-29 after GSD new-project initialization*
