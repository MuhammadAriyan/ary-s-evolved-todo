# CI/CD Setup Guide

## GitHub Actions for Vercel (Frontend)

Vercel auto-connects to GitHub - no manual workflow needed!

### Setup Steps
```
1. Connect repo to Vercel (done during project creation)
2. Vercel automatically:
   - Deploys on push to main
   - Creates preview deploys for PRs
   - Runs builds with env vars
```

### Manual Workflow (Optional)
If you need custom CI before deploy:

```yaml
# .github/workflows/frontend.yml
name: Frontend CI/CD

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'
  pull_request:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci

      - name: Lint
        working-directory: ./frontend
        run: npm run lint

      - name: Type check
        working-directory: ./frontend
        run: npm run type-check

      - name: Build
        working-directory: ./frontend
        env:
          NEXT_PUBLIC_API_URL: ${{ vars.NEXT_PUBLIC_API_URL }}
          NEXT_PUBLIC_APP_URL: ${{ vars.NEXT_PUBLIC_APP_URL }}
        run: npm run build

  # Vercel handles actual deployment via its GitHub integration
```

---

## GitHub Actions for HF Spaces (Backend)

### Setup Steps
```
1. Go to GitHub repo Settings → Secrets and variables → Actions

2. Add Secret:
   HF_TOKEN = your-huggingface-write-token

3. Add Variable:
   HF_SPACE_ID = username/space-name
```

### Workflow File
```yaml
# .github/workflows/backend.yml
name: Backend CI/CD

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'
  pull_request:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        working-directory: ./backend
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        working-directory: ./backend
        env:
          DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
          JWT_SECRET_KEY: test-secret
          CORS_ORIGINS: http://localhost:3000
          BETTER_AUTH_URL: http://localhost:3000
        run: pytest tests/ -v

  deploy:
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to HF Spaces
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
        run: |
          pip install huggingface_hub
          huggingface-cli upload ${{ vars.HF_SPACE_ID }} ./backend . \
            --repo-type space \
            --token $HF_TOKEN

      - name: Wait for rebuild
        run: sleep 60

      - name: Health check
        run: |
          for i in {1..5}; do
            response=$(curl -s -o /dev/null -w "%{http_code}" \
              "https://${{ vars.HF_SPACE_ID }}.hf.space/health" || echo "000")
            if [ "$response" = "200" ]; then
              echo "✅ Backend healthy!"
              exit 0
            fi
            echo "Attempt $i: $response, retrying..."
            sleep 30
          done
          echo "⚠️ Health check timed out"
```

---

## Getting HF Token

```
1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: github-actions
4. Type: Write
5. Copy token immediately (shown only once)
6. Add to GitHub Secrets as HF_TOKEN
```

---

## Vercel Environment Variables in CI

For GitHub Actions that need Vercel env vars:

```yaml
env:
  NEXT_PUBLIC_API_URL: ${{ vars.NEXT_PUBLIC_API_URL }}
```

Add variables in GitHub repo Settings → Secrets and variables → Actions → Variables

---

## Deployment Flow Summary

```
Push to main
    │
    ├─► Frontend (Vercel)
    │   └─► Auto-deploy via Vercel GitHub integration
    │
    └─► Backend (HF Spaces)
        └─► GitHub Action uploads to HF Space
            └─► HF rebuilds Docker image
                └─► Health check verifies deployment
```

---

## Troubleshooting CI/CD

### HF Upload Fails
```
Error: Invalid token
```
**Fix:** Regenerate HF token with Write access, update GitHub secret

### Vercel Build Fails
```
Error: Environment variable not found
```
**Fix:** Add env vars to Vercel dashboard, not just GitHub

### Tests Pass but Deploy Fails
```
Check the deploy job logs separately from test job
```
**Fix:** Ensure `needs: test` is set and test job succeeded
