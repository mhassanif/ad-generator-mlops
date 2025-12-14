# E-Commerce Ad Creative Generator - MLOps Pipeline

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://docs.docker.com/compose/)
[![Airflow](https://img.shields.io/badge/airflow-2.8.1-orange.svg)](https://airflow.apache.org/)
[![MLflow](https://img.shields.io/badge/mlflow-latest-blue.svg)](https://mlflow.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.104-green.svg)](https://fastapi.tiangolo.com/)

An end-to-end MLOps pipeline for generating marketing ad creatives from e-commerce product data using a fine-tuned T5 model. This project demonstrates production-grade ML workflows with orchestration, experiment tracking, model registry, and API serving.

## 📋 Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)

## ✨ Features

### Implemented (6/9 Core Requirements)
- ✅ **Data Ingestion Pipeline**: Automated CSV processing with cleaning and train/test splitting
- ✅ **Generative Model Training**: T5-small fine-tuned for ad creative generation
- ✅ **Experiment Tracking**: MLflow tracking parameters, metrics, and artifacts
- ✅ **Model Registry**: MLflow Model Registry with versioning
- ✅ **Workflow Orchestration**: Airflow DAGs for batch processing and retraining
- ✅ **Model Deployment**: FastAPI REST API serving predictions
- ✅ **Full Containerization**: All services running in Docker

### Pending (Optional)
- ⏳ CI/CD Pipeline (GitHub Actions)
- ⏳ Monitoring & Alerting (Prometheus + Grafana)
- ⏳ Kubernetes Deployment

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose Stack                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │   Airflow    │   │   MLflow     │   │  FastAPI     │    │
│  │  Webserver   │   │   Server     │   │     API      │    │
│  │  :8080       │   │   :5001      │   │   :8000      │    │
│  └──────────────┘   └──────────────┘   └──────────────┘    │
│         │                   │                   │            │
│  ┌──────────────┐          │                   │            │
│  │   Airflow    │          │                   │            │
│  │  Scheduler   │          │                   │            │
│  └──────────────┘          │                   │            │
│         │                   │                   │            │
│  ┌─────────────────────────────────────────────┘            │
│  │              PostgreSQL                                   │
│  │           (Airflow Metadata)                              │
│  └──────────────────────────────────────────────────────────┘
│                                                               │
│  Shared Volumes: code, data, logs, mlflow-artifacts          │
└─────────────────────────────────────────────────────────────┘
```

### Services
1. **Airflow Webserver** (`:8080`) - UI for workflow management
2. **Airflow Scheduler** - Executes DAGs on schedule
3. **PostgreSQL** - Airflow metadata database
4. **MLflow Server** (`:5001`) - Experiment tracking & model registry
5. **FastAPI** (`:8000`) - Model inference API

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- 8GB+ RAM available
- Ports 8080, 5001, 8000 available

### Setup & Run

```bash
# 1. Clone the repository
cd e-commerce-ad-creative-generator-mhassanif

# 2. Create required directories
mkdir -p logs dags config data/processed

# 3. Set permissions
chmod 777 logs

# 4. Configure environment
echo "AIRFLOW_UID=$(id -u)" > .env
echo "_AIRFLOW_WWW_USER_USERNAME=admin" >> .env
echo "_AIRFLOW_WWW_USER_PASSWORD=admin" >> .env

# 5. Start all services
docker-compose up -d

# 6. Wait for initialization (~30 seconds)
docker logs e-commerce-ad-creative-generator-mhassanif-airflow-init-1

# 7. Verify services are running
docker ps
```

### Access Points
- **Airflow UI**: http://localhost:8080 (admin/admin)
- **MLflow UI**: http://localhost:5001
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

## 📁 Project Structure

```
.
├── dags/
│   ├── ingest_dag.py          # Data ingestion orchestration
│   └── train_dag.py           # Model training orchestration
├── src/
│   ├── data/
│   │   └── ingest.py          # Data processing logic
│   ├── models/
│   │   └── train.py           # T5 model training script
│   └── api/
│       └── app.py             # FastAPI application
├── data/
│   ├── raw/                   # Original datasets
│   └── processed/             # Train/test splits
├── docker-compose.yaml        # Service orchestration
├── Dockerfile.api             # API service image
├── Dockerfile.mlflow          # MLflow service image (if needed)
└── requirements.txt           # Python dependencies
```

## 💻 Usage

### 1. Run Data Ingestion

**Via Airflow UI:**
1. Navigate to http://localhost:8080
2. Find `data_ingestion` DAG
3. Toggle to **unpause** (switch to blue)
4. Click **▶️ Trigger DAG**
5. Monitor progress in Graph view

**Result**: Creates `data/processed/train.csv` and `test.csv` (800/200 split)

### 2. Train Model

**Via Airflow UI:**
1. Find `model_training` DAG
2. Toggle to unpause
3. Trigger the DAG
4. Training takes ~5-10 minutes (CPU)
5. Model is automatically registered in MLflow as `ad_creative_t5`

**Check Training Results:**
- Go to http://localhost:5001
- Click "Experiments" → "ad_creative_generation"  
- View metrics (train_loss, val_loss), parameters, and artifacts
- Click "Models" tab to see registered model

### 3. Generate Ad Creatives

**Via API:**

```bash
# Health check
curl http://localhost:8000/health

# Generate ad creative
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Nike",
    "product_name": "Running Shoes"
  }'

# Response
{
  "creative": "Brand: Nike, Name: Running Shoes, No. 1 Running & Running Brand...",
  "brand": "Nike",
  "product_name": "Running Shoes"
}
```

**More Examples:**

```bash
# Apple AirPods
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"brand": "Apple", "product_name": "AirPods Pro"}'

# Samsung Watch
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"brand": "Samsung", "product_name": "Galaxy Watch"}'
```

## 📚 API Documentation

### Endpoints

#### `GET /`
Root endpoint with service information

#### `GET /health`
Health check endpoint
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cpu"
}
```

#### `POST /predict`
Generate ad creative for a product

**Request Body:**
```json
{
  "brand": "string",
  "product_name": "string"
}
```

**Response:**
```json
{
  "creative": "string",
  "brand": "string",
  "product_name": "string"
}
```

**Interactive Docs**: Visit http://localhost:8000/docs for Swagger UI

## 🛠️ Development

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker logs -f e-commerce-ad-creative-generator-mhassanif-api-1
docker logs -f e-commerce-ad-creative-generator-mhassanif-airflow-scheduler-1
```

### Rebuild Services
```bash
# Rebuild specific service
docker-compose build api
docker-compose up -d api

# Rebuild all
docker-compose build
docker-compose up -d
```

### Access Container Shell
```bash
# API container
docker exec -it e-commerce-ad-creative-generator-mhassanif-api-1 bash

# Airflow scheduler
docker exec -it e-commerce-ad-creative-generator-mhassanif-airflow-scheduler-1 bash
```

## 🔧 Configuration

### Environment Variables
Edit `.env` file:
```bash
AIRFLOW_UID=1000
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin
```

### Docker Compose Services
Edit `docker-compose.yaml` to modify:
- Resource limits
- Port mappings
- Volume mounts
- Environment variables

## 📊 MLflow Model Registry

The trained model is registered in MLflow Model Registry:
- **Model Name**: `ad_creative_t5`
- **Version**: Auto-incremented on each training run
- **API Loading**: Automatically loads latest version

To use a specific version in API:
```python
model_uri = "models:/ad_creative_t5/1"  # Version 1
model = mlflow.pytorch.load_model(model_uri)
```

## 🐛 Troubleshooting

### Airflow Init Fails
```bash
# Fix log permissions
sudo chmod -R 777 logs
docker-compose up -d
```

### API Won't Start
```bash
# Check logs
docker logs e-commerce-ad-creative-generator-mhassanif-api-1

# Rebuild
docker-compose build api
docker-compose up -d api
```

### MLflow Can't Find Model
```bash
# Verify model is registered
curl http://localhost:5001/api/2.0/mlflow/registered-models/list

# Re-run training DAG
# Then restart API
docker-compose restart api
```

## 📝 Tech Stack

- **Language**: Python 3.11
- **ML Framework**: PyTorch 2.1.0 (CPU), Transformers 4.36.0
- **Model**: T5-small (fine-tuned)
- **Orchestration**: Apache Airflow 2.8.1
- **Tracking**: MLflow (latest)
- **API**: FastAPI 0.104.1
- **Database**: PostgreSQL 13
- **Containerization**: Docker & Docker Compose

## 📄 License

This project is for educational purposes as part of an MLOps course assignment.

## 👥 Contributors

Hassan - MLOps Implementation

---

**Status**: Phase 4 Complete (6/9 core features) | Ready for monitoring or CI/CD