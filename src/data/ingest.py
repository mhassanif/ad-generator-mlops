import pandas as pd
import os
from sklearn.model_selection import train_test_split
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ingest_data(input_path, output_dir):
    """
    Reads raw CSV, cleans it, and splits into train/test sets.
    """
    logging.info(f"Reading data from {input_path}")
    if not os.path.exists(input_path):
        logging.error(f"Input file not found: {input_path}")
        return

    try:
        df = pd.read_csv(input_path)
        logging.info(f"Loaded {len(df)} rows.")
    except Exception as e:
        logging.error(f"Failed to read CSV: {e}")
        return

    # Basic Cleaning
    # Select relevant columns: product_name, description, brand
    # We will use 'product_name' + 'brand' as input and 'description' as target (Simulating Creative)
    
    needed_cols = ['product_name', 'description', 'brand']
    # Check if columns exist
    if not all(col in df.columns for col in needed_cols):
        logging.error(f"Missing one of required columns: {needed_cols}")
        return

    df = df[needed_cols].dropna()
    logging.info(f"Rows after dropping nulls: {len(df)}")

    # Prepare "Input" text: Brand + Name
    df['input_text'] = "Brand: " + df['brand'].astype(str) + ", Name: " + df['product_name'].astype(str)
    df['target_text'] = df['description'] # Utilizing description as the 'creative' to be learned

    # SAMPLE FOR SPEED (For MLOps Demo Purposes)
    # We limit to 1000 rows to ensure training takes minutes, not hours on CPU.
    if len(df) > 1000:
        df = df.sample(n=1000, random_state=42)
        logging.info("Sampled down to 1000 rows for faster iteration.")

    # Save processed full dataset
    os.makedirs(output_dir, exist_ok=True)
    full_path = os.path.join(output_dir, "processed_full.csv")
    df.to_csv(full_path, index=False)
    logging.info(f"Saved processed data to {full_path}")

    # Split
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    
    train_path = os.path.join(output_dir, "train.csv")
    test_path = os.path.join(output_dir, "test.csv")
    
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    logging.info(f"Saved train set ({len(train_df)}) to {train_path}")
    logging.info(f"Saved test set ({len(test_df)}) to {test_path}")

if __name__ == "__main__":
    INPUT_FILE = "data/raw/flipkart_com-ecommerce_sample.csv"
    OUTPUT_DIR = "data/processed"
    ingest_data(INPUT_FILE, OUTPUT_DIR)
