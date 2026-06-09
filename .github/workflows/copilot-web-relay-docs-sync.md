---
emoji: 📝
description: Detect code changes under 2.copilotWebRelay/ and update documentation to keep docs aligned with source code
on:
  push:
    branches: [main]
    paths:
      - "2.copilotWebRelay/**"
      - "!2.copilotWebRelay/docs/**"
  workflow_dispatch:
permissions:
  contents: read
  pull-requests: read
  issues: read
tools:
  github:
    mode: gh-proxy
    toolsets: [default]
safe-outputs:
  create-pull-request:
    title-prefix: "docs(copilotWebRelay): "
    labels: [documentation]
    draft: true
    allowed-files:
      - "2.copilotWebRelay/docs/**"
---

# Copilot Web Relay Documentation Sync

You are an AI agent responsible for keeping the documentation under `2.copilotWebRelay/docs/` aligned with the source code under `2.copilotWebRelay/`.

## Your Task

When code changes are pushed to `2.copilotWebRelay/`, analyze the current source code and update the documentation to reflect the actual implementation.

## Steps

1. **Read the source code** under `2.copilotWebRelay/`:
   - Entry point files (e.g., `index.js`, `app.js`, `server.js`, `main.py`, etc.)
   - Configuration files (e.g., `config.js`, `config.py`, `.env.example`)
   - Core modules and utility files
   - API route/handler files
   - Any `package.json`, `requirements.txt`, or similar dependency manifests

2. **Read the existing documentation** under `2.copilotWebRelay/docs/` (if any exists).

3. **Compare and identify discrepancies** between the documentation and the actual source code:
   - New endpoints or changed API contracts
   - New or modified modules/classes
   - Changed configuration options
   - New dependencies or changed runtime requirements
   - Updated setup or usage instructions

4. **Update or create documentation files** under `2.copilotWebRelay/docs/`:
   - `2.copilotWebRelay/docs/README.md` — Overview, purpose, and quick start guide
   - `2.copilotWebRelay/docs/api-reference.md` — API endpoints and their request/response formats (if applicable)
   - `2.copilotWebRelay/docs/architecture.md` — Architecture overview (components, data flow, dependencies)
   - `2.copilotWebRelay/docs/configuration.md` — Configuration options and environment variables

5. **Create a pull request** with the documentation updates using `create-pull-request` safe output.
   - Title: `docs(copilotWebRelay): sync documentation with latest code changes`
   - Body should summarize what documentation was updated and why.

## Guidelines

- Write documentation in Japanese (日本語) to match the existing project documentation style.
- Be precise and factual — only document what the code actually does, not what it should do.
- Include code examples where helpful (e.g., API request/response examples, configuration snippets).
- If there are no discrepancies and documentation is up to date, use `noop` with a brief explanation to signal no changes needed.
- Do NOT modify any source code — only create or update files under `2.copilotWebRelay/docs/`.
- Keep documentation concise and well-structured with clear headings.
