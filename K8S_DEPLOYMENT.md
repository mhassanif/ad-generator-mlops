# Kubernetes Deployment Guide

## Prerequisites
- Kubernetes cluster (minikube, GKE, EKS, or AKS)
- kubectl configured
- Docker images pushed to Docker Hub

## Quick Deployment

### 1. Create Namespace
```bash
kubectl apply -f k8s/namespace.yaml
```

### 2. Create ConfigMap
```bash
kubectl apply -f k8s/configmap.yaml
```

### 3. Deploy MLflow
```bash
kubectl apply -f k8s/mlflow-deployment.yaml
```

### 4. Deploy API
```bash
kubectl apply -f k8s/api-deployment.yaml
```

### 5. Verify Deployment
```bash
# Check all resources
kubectl get all -n ad-creative-mlops

# Check pods
kubectl get pods -n ad-creative-mlops

# Check services
kubectl get svc -n ad-creative-mlops
```

### 6. Access API
```bash
# Get external IP (for LoadBalancer)
kubectl get svc api-service -n ad-creative-mlops

# Test API
curl http://<EXTERNAL-IP>/health

# Generate prediction
curl -X POST "http://<EXTERNAL-IP>/predict" \
  -H "Content-Type: application/json" \
  -d '{"brand": "Nike", "product_name": "Shoes"}'
```

## Deploy All at Once
```bash
kubectl apply -f k8s/
```

## Monitor
```bash
# Watch pods
kubectl get pods -n ad-creative-mlops -w

# View logs
kubectl logs -f deployment/api-deployment -n ad-creative-mlops

# Describe pod
kubectl describe pod <POD_NAME> -n ad-creative-mlops
```

## Scale
```bash
# Scale API replicas
kubectl scale deployment api-deployment --replicas=3 -n ad-creative-mlops
```

## Update
```bash
# Update image
kubectl set image deployment/api-deployment api=mhassif/ad-creative-api:v2 -n ad-creative-mlops

# Rollout status
kubectl rollout status deployment/api-deployment -n ad-creative-mlops

# Rollback
kubectl rollout undo deployment/api-deployment -n ad-creative-mlops
```

## Clean Up
```bash
kubectl delete namespace ad-creative-mlops
```

## Minikube Local Testing
```bash
# Start minikube
minikube start

# Deploy
kubectl apply -f k8s/

# Access service
minikube service api-service -n ad-creative-mlops

# Get URL
minikube service api-service -n ad-creative-mlops --url
```
