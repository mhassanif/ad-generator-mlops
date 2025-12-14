# E-Commerce Ad Creative Generator - MLOps Pipeline

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://docs.docker.com/compose/)
[![Airflow](https://img.shields.io/badge/airflow-2.8.1-orange.svg)](https://airflow.apache.org/)
[![MLflow](https://img.shields.io/badge/mlflow-latest-blue.svg)](https://mlflow.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Prometheus](https://img.shields.io/badge/prometheus-latest-orange.svg)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/grafana-latest-orange.svg)](https://grafana.com/)

An end-to-end MLOps pipeline for generating marketing ad creatives from e-commerce product data using a fine-tuned T5 model. Demonstrates production-grade ML workflows with orchestration, experiment tracking, model registry, API serving, and monitoring.

## ✨ Features Implemented

- ✅ **Data Ingestion Pipeline**: Automated CSV processing with cleaning and train/test splitting
- ✅ **Generative Model Training**: T5-small fine-tuned for ad creative generation
- ✅ **Experiment Tracking**: MLflow tracking parameters, metrics, and artifacts
- ✅ **Model Registry**: MLflow Model Registry with version control
- ✅ **Workflow Orchestration**: Airflow DAGs for batch processing and retraining
- ✅ **Model Deployment**: FastAPI REST API with `/predict` endpoint
- ✅ **Monitoring**: Prometheus metrics + Grafana dashboards
- ✅ **Full Containerization**: 7 services orchestrated via Docker Compose

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack (7 Services)          │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌─────────┐  ┌─────────┐  ┌────────────┐     │
│  │ Airflow  │  │ MLflow  │  │   API   │  │ Prometheus │     │
│  │   :8080  │  │  :5001  │  │  :8000  │  │   :9090    │     │
│  └──────────┘  └─────────┘  └─────────┘  └────────────┘     │
│  ┌──────────┐  ┌─────────┐  ┌────────────┐                  │
│  │ Scheduler│  │Postgres │  │  Grafana   │                  │
│  │          │  │         │  │   :3000    │                  │
│  └──────────┘  └─────────┘  └────────────┘                  │
└──────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 8GB+ RAM
- Ports: 8080, 5001, 8000, 9090, 3000 available

### Setup
```bash
# 1. Create environment
mkdir -p logs
chmod 777 logs
echo "AIRFLOW_UID=$(id -u)" > .env

# 2. Start all services
docker-compose up -d

# 3. Wait ~30 seconds for initialization
docker ps  # Verify all 7 containers running
```

### Access Points
| Service | URL | Credentials |
|---------|-----|-------------|
| **Airflow** | http://localhost:8080 | admin/admin |
| **MLflow** | http://localhost:5001 | - |
| **API** | http://localhost:8000/docs | - |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3000 | admin/admin |

## 💻 Usage

### 1. Data Ingestion
```bash
# Via Airflow UI (http://localhost:8080)
1. Unpause `data_ingestion` DAG
2. Trigger DAG
# Creates: data/processed/train.csv (800 rows), test.csv (200 rows)
```

### 2. Model Training
```bash
# Via Airflow UI
1. Unpause `model_training` DAG  
2. Trigger DAG (~5-10 min)
# Registers model "ad_creative_t5" in MLflow Model Registry
```

### 3. Generate Predictions
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"brand": "Nike", "product_name": "Running Shoes"}'

# Response:
{
  "creative": "Brand: Nike, Name: Running Shoes...",
  "brand": "Nike",
  "product_name": "Running Shoes"
}
```

### 4. View Metrics
```bash
# Prometheus metrics
curl http://localhost:8000/metrics

# Grafana dashboards
# Go to: http://localhost:3000
# Explore → Query: api_predictions_total
```

## 📊 Monitoring

### Available Metrics
- `api_predictions_total` - Total predictions made
- `model_inference_seconds` - Inference latency histogram
- `http_requests_total` - HTTP request counter
- `http_request_duration_seconds` - Request latency

### View in Grafana
1. Login: http://localhost:3000 (admin/admin)
2. Click **Explore** (🧭 left sidebar)
3. Query: `api_predictions_total`
4. Click **Run query**

## 📁 Project Structure
```
├── dags/
│   ├── ingest_dag.py          # Data ingestion workflow
│   └── train_dag.py           # Model training workflow
├── src/
│   ├── data/ingest.py         # Data processing
│   ├── models/train.py        # T5 training + MLflow
│   └── api/app.py             # FastAPI + Prometheus metrics
├── monitoring/
│   ├── prometheus.yml         # Prometheus config
│   ├── datasources.yml        # Grafana datasource
│   └── *.json                 # Dashboard templates
├── docker-compose.yaml        # 7-service orchestration
├── Dockerfile.api             # API container
└── requirements.txt           # Python dependencies
```

## 🛠️ Development

### Logs
```bash
docker logs -f e-commerce-ad-creative-generator-mhassanif-api-1
docker logs -f e-commerce-ad-creative-generator-mhassanif-airflow-scheduler-1
```

### Rebuild
```bash
docker-compose build api
docker-compose up -d api
```

### Stop
```bash
docker-compose down
```

## 📊 MLflow Model Registry
- Model: `ad_creative_t5`
- Storage: Artifacts in `/mlflow` volume
- Versioning: Auto-incremented on each training run
- API loads: `models:/ad_creative_t5/latest`

## 📝 Tech Stack
- **ML**: PyTorch 2.1.0 (CPU), Transformers 4.36.0, T5-small
- **Orchestration**: Airflow 2.8.1
- **Tracking**: MLflow (latest)
- **API**: FastAPI 0.104.1 + Uvicorn
- **Monitoring**: Prometheus + Grafana
- **Database**: PostgreSQL 13
- **Containerization**: Docker Compose

## 🐛 Troubleshooting

**Airflow won't start:**
```bash
sudo chmod -R 777 logs
docker-compose up -d
```

**API not loading model:**
```bash
# Verify model exists
curl http://localhost:5001/api/2.0/mlflow/registered-models/list
docker-compose restart api
```

**No metrics in Grafana:**
```bash
# Generate traffic
for i in {1..10}; do curl -s -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"brand": "Nike", "product_name": "Shoes"}' > /dev/null; done
# Check Explore view with: api_predictions_total
```
---
## Demo Video Link
```
https://drive.google.com/file/d/1gncMYUrAAUYqEy0Ws2HmVQk26HiK5RWw/view?usp=drive_link
```