# GitHub Actions Setup Guide

## Required GitHub Secrets

Configure these in: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

### 1. DOCKERHUB_USERNAME
- **Value**: `mhassif` (or your Docker Hub username)
- **Description**: Docker Hub username for pushing images

### 2. DOCKERHUB_TOKEN
- **Value**: Your Docker Hub access token
- **How to get**:
  1. Go to https://hub.docker.com/settings/security
  2. Click "New Access Token"
  3. Name: `github-actions`
  4. Permissions: Read, Write, Delete
  5. Copy the token (you won't see it again!)

### 3. KUBECONFIG
- **Value**: Base64-encoded kubeconfig file
- **Description**: Kubernetes configuration for deployment
- **How to get**:
  ```bash
  # If using DigitalOcean:
  doctl kubernetes cluster kubeconfig show <cluster-name> | base64 -w 0
  
  # If using local kubeconfig:
  cat ~/.kube/config | base64 -w 0
  
  # If using cloud provider CLI:
  # AWS EKS:
  aws eks update-kubeconfig --name <cluster-name>
  cat ~/.kube/config | base64 -w 0
  
  # Google GKE:
  gcloud container clusters get-credentials <cluster-name>
  cat ~/.kube/config | base64 -w 0
  ```

## Workflow Features

### ✅ Automated Build + Test (5 pts)
- Linting with flake8
- Code formatting check with black  
- Unit tests with pytest
- Coverage reporting

### ✅ Automated Docker Image Creation (5 pts)
- Builds Docker image from `Dockerfile.api`
- Pushes to Docker Hub: `mhassif/ad-creative-api:latest`
- Multi-platform builds
- Build caching for faster builds

### ✅ Auto-deployment to Kubernetes (5 pts)
- Deploys only on `main` branch pushes
- Updates Kubernetes deployment with latest image
- Waits for rollout to complete
- Verifies deployment success

### ✅ Security Scanning
- Trivy vulnerability scanner
- Scans for CRITICAL and HIGH vulnerabilities

## Triggering the Workflow

Workflow runs on:
- Push to `main` or `dev` branches
- Pull requests to `main`

**Deployment only happens on `main` branch!**

## Testing Locally Before Push

```bash
# Run tests locally
pytest tests/ -v

# Lint code
flake8 src/

# Build Docker image locally
docker build -f Dockerfile.api -t ad-creative-api:test .

# Test the image
docker run -p 8000:8000 ad-creative-api:test
curl http://localhost:8000/health
```

## First-Time Setup Checklist

- [ ] Add DOCKERHUB_USERNAME secret
- [ ] Add DOCKERHUB_TOKEN secret
- [ ] Add KUBECONFIG secret (if deploying to K8s)
- [ ] Verify Docker Hub repository exists: `mhassif/ad-creative-api`
- [ ] Ensure Kubernetes cluster is accessible
- [ ] Deploy K8s manifests first: `kubectl apply -f k8s/`
- [ ] Push to `main` branch to trigger workflow

## Monitoring Workflow

1. Go to **Actions** tab in GitHub
2. Click on latest workflow run
3. Expand each job to see logs
4. Check for:
   - ✅ Tests passing
   - ✅ Docker image pushed
   - ✅ Deployment successful

## Troubleshooting

**Tests failing?**
- Check test logs in Actions tab
- Run `pytest tests/ -v` locally

**Docker push failing?**
- Verify DOCKERHUB_USERNAME and DOCKERHUB_TOKEN secrets
- Check Docker Hub permissions

**K8s deployment failing?**
- Verify KUBECONFIG secret is correct
- Ensure cluster is accessible
- Check namespace exists: `kubectl get ns ad-creative`
- Verify deployment exists: `kubectl get deployment -n ad-creative`

## Notes

- Kubernetes deployment requires cluster to be running
- For demo without K8s, comment out the `deploy-to-kubernetes` job
- Tests use TestClient so no actual model loading needed for CI
