# End-to-End Pipeline Test

## Goal
Verify the complete MLOps pipeline works end-to-end with artifact logging.

## Test Steps

### 1. Verify Services Running
```bash
docker ps
```
Expected: All 4 containers running (postgres, mlflow, airflow-webserver, airflow-scheduler)

### 2. Test Data Ingestion DAG
1. Go to http://localhost:8080
2. Login: admin/admin
3. Unpause `data_ingestion` DAG
4. Trigger manually
5. **Expected Result**: ✅ Green - data in `data/processed/`

### 3. Test Model Training DAG (Full Artifacts)
1. Unpause `model_training` DAG  
2. Trigger manually
3. Watch logs - should see:
   - "Loading tokenizer..."
   - "Training epoch 1/3..." 
   - "Model logged to MLflow Model Registry"
   - "Tokenizer logged to MLflow"
4. **Expected Result**: ✅ Green - ~5-10 mins

### 4. Verify MLflow Artifacts
1. Go to http://localhost:5001
2. Click "ad_creative_generation" experiment
3. Click the latest run
4. **Check Artifacts tab** - should see:
   - `dataset/train.csv`
   - `dataset/test.csv`
   - `model/` (PyTorch model)
   - `tokenizer/` (tokenizer files)
5. **Check Metrics** - should see:
   - train_loss (per epoch)
   - val_loss
6. **Check Parameters** - should see:
   - epochs, batch_size, learning_rate, model_type

### 5. Verify Model Registry
1. In MLflow UI, click "Models" tab (top)
2. Should see "ad_creative_t5" registered model
3. Click it to see versions

## Success Criteria
- ✅ Both DAGs complete successfully
- ✅ All artifacts present in MLflow
- ✅ Model registered in Model Registry
- ✅ Metrics and parameters logged

## Next: Phase 4
Once verified, proceed to FastAPI deployment which will load the model from MLflow Model Registry.
