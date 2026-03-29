---
phase: 02-quality-extensibility
plan: 02
subsystem: infra
tags: [nginx, tls, oci, self-hosted-runner, curl-smoke]

requires:
  - phase: 02-quality-extensibility
    provides: ROADMAP scope for VM baseline
provides:
  - README runbook for Nginx reverse proxy, OpenSSL IP SAN, OCI ports, HTTPS smoke tests
affects: [02-03-PLAN]

tech-stack:
  added: []
  patterns: ["Document placeholder PUBLIC_IP for operator substitution"]

key-files:
  created: []
  modified:
    - README.md

key-decisions:
  - "Self-signed TLS with subjectAltName=IP:PUBLIC_IP; public smoke uses curl -k to https://PUBLIC_IP/health."

patterns-established:
  - "proxy_pass to http://127.0.0.1:5000 with X-Forwarded-* headers in README."

requirements-completed: [VM-DEPLOY]

duration: 25min
completed: 2026-03-29
---

# Phase 2: quality-extensibility — Plan 02 Summary

**README extended with Nginx TLS (IP SAN), OCI ingress 22/80/443, and HTTPS smoke commands aligned to `build-publish.yml` port 5000.**

## Performance

- **Duration:** ~25 min
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Sections 2.3.2–2.3.4 document install paths, OpenSSL, server block, firewall, and curl examples.
- Runner section 2.3.1 clarifies comma-separated labels, `svc.sh`, and docker group + session refresh.

## Task Commits

1. **Task 1: VM operator section** — (see git)

## Files Created/Modified

- `README.md` — Nginx, TLS, smoke tests, OCI ports.

## Deviations from Plan

None.

## Issues Encountered

None.

## Next Phase Readiness

Production env documentation (02-03) can reference this runbook and `.env.example`.

---
*Phase: 02-quality-extensibility*
*Completed: 2026-03-29*
