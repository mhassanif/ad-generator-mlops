import mlflow.pytorch
from transformers import T5Tokenizer
import torch

def predict(brand, product_name):
    # Load the model from the latest MLflow run
    # In a real scenario, we would use the Run ID, but for now we pick the latest from default experiment
    runs = mlflow.search_runs(experiment_names=["ad_creative_generation"])
    if runs.empty:
        print("No runs found.")
        return
    
    # Get latest run
    latest_run_id = runs.iloc[0].run_id
    print(f"Loading model from Run ID: {latest_run_id}")
    
    # Load model
    model_uri = f"runs:/{latest_run_id}/model"
    model = mlflow.pytorch.load_model(model_uri)
    
    # Load Tokenizer (we saved this locally, but good practice to load from artifact if possible)
    # For simplicity, loading from local folder we saved
    tokenizer = T5Tokenizer.from_pretrained("tokenizer_files")
    
    # Prepare Input
    input_text = f"Brand: {brand}, Name: {product_name}"
    encoding = tokenizer(input_text, return_tensors="pt")
    input_ids = encoding.input_ids
    attention_mask = encoding.attention_mask
    
    # Generate
    # Added min_length to force output, and adjusted beam search
    outputs = model.generate(
        input_ids, 
        attention_mask=attention_mask,
        max_length=64, 
        min_length=10, 
        num_beams=4, 
        early_stopping=True,
        no_repeat_ngram_size=2
    )
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    print(f"\nInput: {input_text}")
    print(f"Generated Creative: {generated_text}\n")

if __name__ == "__main__":
    predict("Nike", "Air Max Running Shoes")
    predict("Apple", "MacBook Pro M3")
