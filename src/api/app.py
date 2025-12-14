"""
FastAPI service for Ad Creative Generation
Loads model from MLflow Model Registry and serves predictions
With Prometheus metrics for monitoring
"""
import os
import logging
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram
import mlflow
import mlflow.pyfunc
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="E-Commerce Ad Creative Generator",
    description="Generate marketing creatives for e-commerce products",
    version="1.0.0"
)

# Initialize Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Custom metrics
prediction_counter = Counter(
    'api_predictions_total',
    'Total number of predictions made'
)
inference_duration = Histogram(
    'model_inference_seconds',
    'Time spent on model inference',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Global variables for model and tokenizer
model = None
tokenizer = None
device = None

class PredictRequest(BaseModel):
    brand: str
    product_name: str
    
    class Config:
        schema_extra = {
            "example": {
                "brand": "Nike",
                "product_name": "Running Shoes"
            }
        }

class PredictResponse(BaseModel):
    creative: str
    brand: str
    product_name: str

@app.on_event("startup")
async def load_model():
    """Load model from MLflow Model Registry on startup"""
    global model, tokenizer, device
    
    try:
        # Set MLflow tracking URI (localhost for local dev, mlflow:5000 in Docker)
        mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5001")
        mlflow.set_tracking_uri(mlflow_uri)
        logger.info(f"MLflow URI: {mlflow_uri}")
        
        # Load model from Model Registry
        model_name = "ad_creative_t5"
        model_version = "latest"
        model_uri = f"models:/{model_name}/{model_version}"
        
        logger.info(f"Loading model from: {model_uri}")
        
        # Load PyTorch model
        model = mlflow.pytorch.load_model(model_uri)
        model.eval()
        
        # Load tokenizer
        tokenizer = T5Tokenizer.from_pretrained("t5-small")
        
        # Set device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)
        
        logger.info(f"Model loaded successfully on {device}")
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Ad Creative Generator API",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health():
    """Health check endpoint"""
    model_loaded = model is not None and tokenizer is not None
    return {
        "status": "healthy" if model_loaded else "unhealthy",
        "model_loaded": model_loaded,
        "device": str(device) if device else "not set"
    }

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    """
    Generate ad creative for a product
    
    Args:
        request: PredictRequest with brand and product_name
        
    Returns:
        PredictResponse with generated creative
    """
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Increment prediction counter
    prediction_counter.inc()
    
    try:
        # Create input text
        input_text = f"Brand: {request.brand}, Name: {request.product_name}"
        logger.info(f"Generating creative for: {input_text}")
        
        # Start inference timer
        start_time = time.time()
        
        # Tokenize input
        encoding = tokenizer(
            input_text,
            return_tensors="pt",
            max_length=128,
            padding=True,
            truncation=True
        )
        
        # Move to device
        input_ids = encoding.input_ids.to(device)
        attention_mask = encoding.attention_mask.to(device)
        
        # Generate creative
        with torch.no_grad():
            outputs = model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_length=64,
                min_length=10,
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=2,
                temperature=0.7
            )
        
        # Decode output
        creative = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Record inference duration
        inference_time = time.time() - start_time
        inference_duration.observe(inference_time)
        
        logger.info(f"Generated in {inference_time:.2f}s: {creative}")
        
        return PredictResponse(
            creative=creative,
            brand=request.brand,
            product_name=request.product_name
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
