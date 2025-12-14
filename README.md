[![R# Intelligent E-Commerce Ad Creative Generator

## Project Overview
Automated system to generate marketing creatives (text) for e-commerce products using Generative AI. This project demonstrates a production-grade MLOps pipeline including Airflow, MLflow, Docker, Kubernetes, and Prometheus/Grafana.

## Setup Instructions

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Git

### Local Environment Setup
1. **Initialize Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run Data Ingestion**:
   ```bash
   python src/data/ingest.py
   ```

3. **Run Model Training**:
   ```bash
   python src/models/train.py --epochs 3
   ```
   > **Note**: Start the MLflow UI in a separate terminal with `mlflow ui` to view training metrics.

4. **Verify Model**:
   ```bash
   python src/predict_test.py
   ```

5. **Orchestration (Airflow & Docker)**:
   Run the entire stack (Airflow, MLflow, Postgres) using Docker:
   ```bash
   docker-compose up --build -d
   ```
   - **Airflow UI**: [http://localhost:8080](http://localhost:8080) (User/Pass: `admin`/`admin`)
   - **MLflow UI**: [http://localhost:5001](http://localhost:5001)

   To stop:
   ```bash
   docker-compose down
   ```



[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/EsmaCwYg)