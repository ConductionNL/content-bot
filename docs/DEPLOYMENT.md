# Conduction Content Bot deployment (image → GHCR → Helm → ArgoCD)

Repo-specific deployment guide for the Slack Socket Mode content bot.

## Container and runtime
- App: Slack Bolt Socket Mode (no HTTP server). Entrypoint: `python -m conduction_content_bot`.
- Image does not expose ports; tokens are provided via env vars.

Local smoke test
```bash
docker build -t conduction-content-bot .
docker run --rm --env-file .env conduction-content-bot
# Check logs: should connect to Slack Socket Mode successfully.
```

## GitHub Actions → GHCR
Workflow file: `.github/workflows/docker-publish.yml`
- Publishes to `ghcr.io/<owner>/conduction-content-bot`
- Tags: branch, tag, sha; `:latest` on default branch

Make GHCR package public
- GitHub → Org → Packages → conduction-content-bot → Settings → Visibility → Public
- Or keep private and authenticate cluster with a PAT or GHCR secret

PAT login (private images)
```bash
echo <PAT> | docker login ghcr.io -u <GITHUB_USERNAME> --password-stdin
```

## Helm chart (charts/content-bot)
This bot runs without a Service/Ingress (outbound only). Configure env vars.

Minimal values
```yaml
image:
  repository: ghcr.io/conductionnl/conduction-content-bot
  tag: latest
  pullPolicy: IfNotPresent

env:
  SLACK_APP_TOKEN: xapp-...
  SLACK_BOT_TOKEN: xoxb-...
  OPENAI_API_KEY: sk-...
  OPENAI_MODEL: gpt-5-mini
  WEBSITE_BASE_URL: https://conduction.nl
```

Install/upgrade
```bash
helm upgrade --install content-bot charts/content-bot \
  --namespace content-bot --create-namespace \
  --set image.repository=ghcr.io/conductionnl/conduction-content-bot \
  --set image.tag=latest
```

## ArgoCD
- repoURL: `https://github.com/ConductionNL/content-bot.git`
- revision: `main` (or pin a tag/sha)
- path: `charts/content-bot`
- namespace: `content-bot` (CreateNamespace)
- values: set tokens via ArgoCD values or ExternalSecret

## Notes / Troubleshooting
- Image pull denied → package private or missing credentials
- Bot not connecting → verify `SLACK_APP_TOKEN` (xapp-...) and `SLACK_BOT_TOKEN` (xoxb-...)
- OpenAI errors → check `OPENAI_API_KEY` and model name
- No ports needed; ensure egress to Slack and OpenAI is allowed by NetworkPolicy/proxy
