# Deployment guide (container → GHCR → Helm → ArgoCD)

This file is meant to be copy-paste friendly for other repos.

## Container and runtime
- App: Slack Socket Mode bot for content generation
- No HTTP ports exposed; outbound connection to Slack (no Service/Ingress)
- Credentials provided via environment/Secret: `OPENAI_API_KEY`, `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`

Local smoke test
```bash
# Run the bot locally in a container (requires valid Slack/OpenAI secrets)
docker run --rm \
  -e OPENAI_API_KEY=... \
  -e SLACK_BOT_TOKEN=xoxb-... \
  -e SLACK_APP_TOKEN=xapp-... \
  ghcr.io/conductionnl/conduction-content-bot:latest
# Watch logs for a successful Slack Socket Mode connection; Ctrl+C to stop
```

## GitHub Actions → GHCR
Workflow file: `.github/workflows/docker-publish.yml`
- **CI workflow**: Runs on PRs and main (lint, test, build)
- **Publish workflow**: Runs after CI succeeds on main only
- Publishes to `ghcr.io/<owner>/conduction-content-bot`
- **Immutable tags**: Uses `sha-<shortsha>` for deterministic deployments
- **Automated bump**: Updates `charts/content-bot/values.yaml` with new image tag
- **Retention**: Keeps last 30 images, cleans up older ones weekly

### CI/CD Flow
1. **PR**: Only CI runs (lint, test, build)
2. **Main**: CI runs → Publish runs (builds/pushes `sha-<shortsha>` + `latest`) → Bump step updates Git
3. **Argo CD**: Auto-syncs to Git changes, deploys immutable tag

### Workflow Structure
```yaml
# CI workflow (.github/workflows/ci.yml)
name: CI
on:
  push:
    branches: [ main ]
  pull_request:
jobs:
  build-and-lint:
    if: ${{ github.actor != 'github-actions[bot]' && !contains(github.event.head_commit.message, '[skip ci]') }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .[dev]
      - name: Lint (ruff)
        run: ruff check src
      - name: Format check (black)
        run: black --check src
      - name: Build Docker image
        run: docker build -f dockerfile -t conduction-content-bot:ci .

# Publish workflow (.github/workflows/docker-publish.yml)  
name: Publish Docker image to GHCR
on:
  workflow_run:
    workflows: [ "CI" ]
    types: [ completed ]
  workflow_dispatch:
jobs:
  build-and-push:
    if: ${{ github.event.workflow_run.conclusion == 'success' && github.event.workflow_run.head_branch == 'main' }}
    runs-on: ubuntu-latest
    permissions:
      contents: write
      packages: write
      id-token: write
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.workflow_run.head_sha }}
      - uses: docker/setup-qemu-action@v3
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Compute tags
        shell: bash
        run: |
          SHORT_SHA=$(echo "${{ github.event.workflow_run.head_sha }}" | cut -c1-7)
          OWNER_LC=$(echo "${{ github.repository_owner }}" | tr '[:upper:]' '[:lower:]')
          echo "TAGS=ghcr.io/${OWNER_LC}/conduction-content-bot:sha-${SHORT_SHA},ghcr.io/${OWNER_LC}/conduction-content-bot:latest" >> $GITHUB_ENV
      - uses: docker/build-push-action@v6
        with:
          context: .
          file: dockerfile
          push: true
          tags: ${{ env.TAGS }}
          labels: org.opencontainers.image.revision=${{ github.event.workflow_run.head_sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - name: Install yq
        shell: bash
        run: |
          sudo curl -L https://github.com/mikefarah/yq/releases/download/v4.44.3/yq_linux_amd64 -o /usr/local/bin/yq
          sudo chmod +x /usr/local/bin/yq
      - name: Bump Helm image.tag to commit SHA and push to main [skip ci]
        shell: bash
        run: |
          SHORT_SHA=$(echo "${{ github.event.workflow_run.head_sha }}" | cut -c1-7)
          TAG="sha-${SHORT_SHA}"
          yq eval ".image.tag = \"${TAG}\"" -i charts/content-bot/values.yaml
          git config user.name "github-actions"
          git config user.email "github-actions@github.com"
          git fetch origin main
          git checkout -B main origin/main
          git add charts/content-bot/values.yaml
          git diff --cached --quiet || git commit -m "chore: bump image tag to ${TAG} [skip ci]"
          git push origin main
```

## Helm chart (charts/content-bot)
Minimal values we used (no Service is exposed; bot runs in Slack Socket Mode)
```yaml
image:
  repository: ghcr.io/conductionnl/conduction-content-bot
  tag: sha-<shortsha>  # Set automatically by CI bump step
  pullPolicy: IfNotPresent  # Immutable tags don't need Always

replicaCount: 1

# Load all keys from a Secret as environment variables
secretRef: "content-bot-secrets"

# Optional (non-secret) key/values
env:
  OPENAI_MODEL: gpt-5-mini
  OPENAI_TIMEOUT_SECONDS: "30"
  OPENAI_MAX_RETRIES: "5"
  LLM_BACKOFF_BASE_SECONDS: "1.0"
  LLM_BACKOFF_MAX_SECONDS: "15.0"
  HISTORY_MAX_MESSAGES: "10"
  WEBSITE_BASE_URL: https://conduction.nl
```

## Secrets
Add env secrets as kubernetes Secrets so that the app has access to them
```bash
# Create Secret with required keys
kubectl -n content-bot create secret generic content-bot-secrets \
  --from-literal=OPENAI_API_KEY='...' \
  --from-literal=SLACK_BOT_TOKEN='...' \
  --from-literal=SLACK_APP_TOKEN='...'
```

## ArgoCD (CLI)
```bash
# Create the Application (adjust dest-server for your cluster)
argocd app create content-bot \
  --project default \
  --repo https://github.com/ConductionNL/content-bot.git \
  --path charts/content-bot \
  --revision main \
  --dest-server <cluster-api-or-https://kubernetes.default.svc> \
  --dest-namespace content-bot \
  --sync-policy automated --self-heal --auto-prune \
  --helm-set image.repository=ghcr.io/conductionnl/conduction-content-bot \
  --helm-set secretRef=content-bot-secrets

# Sync
argocd app sync content-bot 
```

No Service exposed
- The bot uses Slack Socket Mode and does not create a Service or Ingress.

## ArgoCD (UI)
- repoURL: `https://github.com/ConductionNL/content-bot.git`
- revision: `main` (use the branch that contains `charts/content-bot`)
- path: `charts/content-bot`
- namespace: `content-bot` (enable CreateNamespace)
- values: set `secretRef: content-bot-secrets`; image.tag is managed automatically by CI

If ArgoCD cannot access the repo, add it under Settings → Repositories (HTTPS with PAT or SSH), then create/sync the Application. When ArgoCD manages the app, avoid also installing it manually with Helm CLI (uninstall the manual release first to prevent ownership conflicts).

### Immutable deployments
- CI automatically updates `image.tag` to `sha-<shortsha>` in Git
- Argo CD syncs to Git changes and deploys the exact image
- No manual parameter overrides needed; Git values take precedence
- `imagePullPolicy: IfNotPresent` is sufficient with immutable tags

## Troubleshooting
- denied on docker pull → package private or PAT/SSO missing
- manifest unknown → tag not published yet (rerun workflow)
- Argo error "can't evaluate field additional" → ensure `env:` is a map (don't set `env` to a string or list)
- Argo repo not accessible → register the repo in ArgoCD Settings → Repositories (or use CLI to add)
- Empty image tag → check if Argo CD has parameter overrides; remove them to use Git values
- Bump step fails → check yq syntax and git checkout commands in workflow logs

## Quick checks
```bash
# View logs
kubectl -n content-bot logs deploy/content-bot-content-bot -f

# Inspect objects
kubectl -n content-bot get deploy,rs,pod

# Check current image tag
kubectl -n content-bot get deploy content-bot-content-bot -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'

# Check Argo CD sync status
argocd app get content-bot --grpc-web
```