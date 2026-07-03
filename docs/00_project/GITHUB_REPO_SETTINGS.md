# GitHub repository settings — copy/paste

Apply these in **GitHub → Repository → Settings → General** (About) and **Topics**.

## About — Description

```
Portfolio: GitHub-first agentic SDLC case study (v0.1). Demo app: synthetic support-ticket triage. Start: docs/00_project/PORTFOLIO_TOUR.md
```

## About — Website (optional)

Link to the portfolio tour on GitHub:

```
https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/blob/main/docs/00_project/PORTFOLIO_TOUR.md
```

## Topics

Add these (GitHub allows up to 20):

```
ai-agents
agentic-ai
sdlc
github-actions
mcp
pytest
llm
portfolio
fastapi
python
```

## CLI (alternative to UI)

```powershell
gh repo edit raghuram-chittibomma/support-ticket-triage-assistant `
  --description "Portfolio: GitHub-first agentic SDLC case study (v0.1). Demo app: synthetic support-ticket triage. Start: docs/00_project/PORTFOLIO_TOUR.md" `
  --homepage "https://github.com/raghuram-chittibomma/support-ticket-triage-assistant/blob/main/docs/00_project/PORTFOLIO_TOUR.md" `
  --add-topic ai-agents --add-topic agentic-ai --add-topic sdlc `
  --add-topic github-actions --add-topic mcp --add-topic pytest `
  --add-topic llm --add-topic portfolio --add-topic fastapi --add-topic python
```

## Release v0.1.0 body

After merging the Phase 1 PR, refresh the release notes (delivery-first):

```powershell
gh release edit v0.1.0 --notes-file docs/00_project/RELEASE_v0.1.0_BODY.md
```

(See `RELEASE_v0.1.0_BODY.md` in this folder for the file contents.)
