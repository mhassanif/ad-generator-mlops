import pandas as pd
import mlflow
import mlflow.pytorch
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import T5Tokenizer, T5ForConditionalGeneration, AdamW
import logging
import argparse
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('training.log')
    ]
)

class AdCreativeDataset(Dataset):
    def __init__(self, csv_path, tokenizer, max_length=128):
        self.data = pd.read_csv(csv_path)
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Ensure correct columns exist
        if 'input_text' not in self.data.columns or 'target_text' not in self.data.columns:
            raise ValueError("CSV must contain 'input_text' and 'target_text' columns")
        
        logging.info(f"Loaded dataset with {len(self.data)} samples from {csv_path}")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        
        input_enc = self.tokenizer(
            str(row['input_text']),
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors="pt"
        )
        
        target_enc = self.tokenizer(
            str(row['target_text']),
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors="pt"
        )

        return {
            'input_ids': input_enc.input_ids.flatten(),
            'attention_mask': input_enc.attention_mask.flatten(),
            'labels': target_enc.input_ids.flatten()
        }

def train(data_dir, epochs=3, batch_size=8, lr=5e-5):
    try:
        # MLflow Setup
        mlflow_tracking_uri = os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5001')
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        mlflow.set_experiment("ad_creative_generation")
        
        logging.info(f"MLflow tracking URI: {mlflow_tracking_uri}")
        
        with mlflow.start_run():
            logging.info("Starting MLflow run...")
            
            # Log Params
            mlflow.log_params({
                "epochs": epochs,
                "batch_size": batch_size,
                "learning_rate": lr,
                "model_type": "t5-small",
                "data_source": data_dir
            })
            
            # Verify data files exist
            train_path = os.path.join(data_dir, "train.csv")
            test_path = os.path.join(data_dir, "test.csv")
            
            if not os.path.exists(train_path):
                raise FileNotFoundError(f"Training data not found at {train_path}")
            if not os.path.exists(test_path):
                raise FileNotFoundError(f"Test data not found at {test_path}")
            
            # Log Dataset for Versioning
            mlflow.log_artifact(train_path, artifact_path="dataset")
            mlflow.log_artifact(test_path, artifact_path="dataset")
            
            # Load Data
            logging.info("Loading tokenizer and datasets...")
            tokenizer = T5Tokenizer.from_pretrained("t5-small")
            train_dataset = AdCreativeDataset(train_path, tokenizer)
            test_dataset = AdCreativeDataset(test_path, tokenizer)
            
            train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
            test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
            
            # Model Setup
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logging.info(f"Using device: {device}")
            
            model = T5ForConditionalGeneration.from_pretrained("t5-small").to(device)
            optimizer = AdamW(model.parameters(), lr=lr)
            
            logging.info(f"Training on {device} for {epochs} epochs...")
            
            # Training Loop
            model.train()
            for epoch in range(epochs):
                total_loss = 0
                batch_count = 0
                
                for batch in train_loader:
                    try:
                        input_ids = batch['input_ids'].to(device)
                        attention_mask = batch['attention_mask'].to(device)
                        labels = batch['labels'].to(device)
                        
                        outputs = model(
                            input_ids=input_ids,
                            attention_mask=attention_mask,
                            labels=labels
                        )
                        
                        loss = outputs.loss
                        total_loss += loss.item()
                        batch_count += 1
                        
                        optimizer.zero_grad()
                        loss.backward()
                        optimizer.step()
                        
                        if batch_count % 10 == 0:
                            logging.info(f"Epoch {epoch+1}/{epochs} - Batch {batch_count}/{len(train_loader)} - Loss: {loss.item():.4f}")
                    
                    except Exception as e:
                        logging.error(f"Error in training batch: {e}")
                        continue
                
                avg_loss = total_loss / len(train_loader)
                logging.info(f"Epoch {epoch+1}/{epochs} - Average Loss: {avg_loss:.4f}")
                mlflow.log_metric("train_loss", avg_loss, step=epoch)
                
                # Validation
                model.eval()
                val_loss = 0
                with torch.no_grad():
                    for batch in test_loader:
                        try:
                            input_ids = batch['input_ids'].to(device)
                            attention_mask = batch['attention_mask'].to(device)
                            labels = batch['labels'].to(device)
                            
                            outputs = model(
                                input_ids=input_ids,
                                attention_mask=attention_mask,
                                labels=labels
                            )
                            val_loss += outputs.loss.item()
                        except Exception as e:
                            logging.error(f"Error in validation batch: {e}")
                            continue
                
                avg_val_loss = val_loss / len(test_loader)
                logging.info(f"Epoch {epoch+1}/{epochs} - Validation Loss: {avg_val_loss:.4f}")
                mlflow.log_metric("val_loss", avg_val_loss, step=epoch)
                model.train()
            
            # Save Model to MLflow
            logging.info("Saving model to MLflow...")
            
            # Save model
            mlflow.pytorch.log_model(
                model,
                "model",
                registered_model_name="ad_creative_t5"
            )
            
            # Save tokenizer as artifact
            tokenizer_dir = "tokenizer_files"
            os.makedirs(tokenizer_dir, exist_ok=True)
            tokenizer.save_pretrained(tokenizer_dir)
            mlflow.log_artifacts(tokenizer_dir, artifact_path="tokenizer")
            
            logging.info("Training Complete.")
            logging.info(f"Run ID: {mlflow.active_run().info.run_id}")
            
            return True
            
    except Exception as e:
        logging.error(f"Training failed: {e}")
        import traceback
        logging.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="data/processed")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--lr", type=float, default=5e-5)
    args = parser.parse_args()
    
    train(args.data_dir, epochs=args.epochs, batch_size=args.batch_size, lr=args.lr)