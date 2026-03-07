# Pull Request

**PR para `homolog`:** features e correções. **PR para `main`:** apenas release a partir de homolog (time CODEOWNERS).

## Description

<!-- Briefly describe WHAT was changed and WHY. -->

## Type of change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that changes existing behavior)
- [ ] Refactoring / code improvement (no functional change)
- [ ] CI/CD / infrastructure change
- [ ] Documentation update

## Related issue

<!-- Closes #<issue-number> -->

## Checklist

- [ ] Tests were added / updated for the changes
- [ ] All new tests pass locally (`pytest`)
- [ ] `pre-commit run --all-files` runs clean (Black, isort, Ruff, mypy)
- [ ] No new secrets or credentials committed (check `.env` is not staged)
- [ ] `.env.example` updated if new environment variables were added
- [ ] Documentation / README updated if necessary
- [ ] PR title follows conventional commits format (`feat:`, `fix:`, `chore:`, etc.)

## Security considerations

<!-- Does this PR introduce changes that could affect security?
     If yes, describe the risk and how it was mitigated. -->

## Screenshots / logs (if applicable)

<!-- Add screenshots or relevant log output here. -->
