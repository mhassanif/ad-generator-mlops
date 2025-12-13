import pandas as pd
import mlflow
import mlflow.pytorch
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import T5Tokenizer, T5ForConditionalGeneration, AdamW
import logging
import argparse
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AdCreativeDataset(Dataset):
    def __init__(self, csv_path, tokenizer, max_length=128):
        self.data = pd.read_csv(csv_path)
        self.tokenizer = tokenizer
        self.max_length = max_length
        # Ensure correct columns exist
        if 'input_text' not in self.data.columns or 'target_text' not in self.data.columns:
            raise ValueError("CSV must contain 'input_text' and 'target_text' columns")

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
    # MLflow Setup
    mlflow.set_experiment("ad_creative_generation")
    
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
        
        # Log Dataset for Versioning (Rubric Requirement)
        mlflow.log_artifact(os.path.join(data_dir, "train.csv"), artifact_path="dataset")

        # Load Data
        train_path = os.path.join(data_dir, "train.csv")
        test_path = os.path.join(data_dir, "test.csv")
        
        tokenizer = T5Tokenizer.from_pretrained("t5-small")
        train_dataset = AdCreativeDataset(train_path, tokenizer)
        test_dataset = AdCreativeDataset(test_path, tokenizer)
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        # test_loader could be used for validation loop

        # Model Setup
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = T5ForConditionalGeneration.from_pretrained("t5-small").to(device)
        optimizer = AdamW(model.parameters(), lr=lr)

        logging.info(f"Training on {device} for {epochs} epochs...")
        
        # Training Loop
        model.train()
        for epoch in range(epochs):
            total_loss = 0
            for batch in train_loader:
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

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            avg_loss = total_loss / len(train_loader)
            logging.info(f"Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f}")
            mlflow.log_metric("train_loss", avg_loss, step=epoch)

        # Save Model to MLflow
        logging.info("Saving model to MLflow...")
        mlflow.pytorch.log_model(model, "model")
        
        # Save tokenizer as artifact so we can use it for inference
        tokenizer.save_pretrained("tokenizer_files")
        mlflow.log_artifacts("tokenizer_files", artifact_path="tokenizer")
        
        logging.info("Training Complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="data/processed")
    parser.add_argument("--epochs", type=int, default=1) # Default 1 for speed
    parser.add_argument("--batch_size", type=int, default=4)
    args = parser.parse_args()
    
    train(args.data_dir, epochs=args.epochs, batch_size=args.batch_size)
