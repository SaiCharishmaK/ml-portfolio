# src/preprocessing_pipeline.py
"""
Standalone preprocessing pipeline.
Called by Airflow DAG in Phase 8.
"""
import os
import re
import json
import torch
import boto3
import pandas as pd
import numpy as np
from transformers import DistilBertTokenizer
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv(
    'MODEL_NAME', 'distilbert-base-uncased')
MAX_LENGTH = int(os.getenv('MAX_LENGTH', 128))
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 16))

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv(
            'AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv(
            'AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv(
            'AWS_DEFAULT_REGION')
    )

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\b\d{10,}\b', '[NUM]', text)
    return text

def load_from_s3(bucket):
    s3 = get_s3_client()
    os.makedirs('data/raw', exist_ok=True)

    for filename in ['ag_news_train.csv',
                     'ag_news_test.csv']:
        s3.download_file(
            bucket,
            f'raw/{filename}',
            f'data/raw/{filename}'
        )

    df_train = pd.read_csv('data/raw/ag_news_train.csv')
    df_test  = pd.read_csv('data/raw/ag_news_test.csv')
    return df_train, df_test

def tokenize_texts(texts, tokenizer,
                   max_length, batch_size=512):
    all_ids, all_masks = [], []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size].tolist()
        enc   = tokenizer(
            batch,
            max_length=max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        all_ids.append(enc['input_ids'])
        all_masks.append(enc['attention_mask'])
    return (torch.cat(all_ids),
            torch.cat(all_masks))

def run_pipeline():
    print("Starting preprocessing pipeline...")
    bucket    = os.getenv('S3_BUCKET_DATA')
    tokenizer = DistilBertTokenizer\
        .from_pretrained(MODEL_NAME)

    df_train, df_test = load_from_s3(bucket)

    df_train['text_clean'] = df_train[
        'text'].apply(clean_text)
    df_test['text_clean']  = df_test[
        'text'].apply(clean_text)

    X_tr, X_val, y_tr, y_val = train_test_split(
        df_train['text_clean'].values,
        df_train['label'].values,
        test_size=0.1,
        random_state=42,
        stratify=df_train['label'].values
    )

    X_test = df_test['text_clean'].values
    y_test = df_test['label'].values

    print("Tokenizing datasets...")
    train_ids, train_mask = tokenize_texts(
        X_tr, tokenizer, MAX_LENGTH)
    val_ids,   val_mask   = tokenize_texts(
        X_val, tokenizer, MAX_LENGTH)
    test_ids,  test_mask  = tokenize_texts(
        X_test, tokenizer, MAX_LENGTH)

    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('models/tokenizer', exist_ok=True)

    for name, ids, mask, labels in [
        ('train', train_ids, train_mask,
         torch.tensor(y_tr)),
        ('val',   val_ids,   val_mask,
         torch.tensor(y_val)),
        ('test',  test_ids,  test_mask,
         torch.tensor(y_test))
    ]:
        path = f'data/processed/{name}_tensors.pt'
        torch.save({
            'input_ids':      ids,
            'attention_mask': mask,
            'labels':         labels
        }, path)
        print(f"✅ Saved {path}")

    tokenizer.save_pretrained(
        'models/tokenizer')
    print("✅ Preprocessing complete")

if __name__ == "__main__":
    run_pipeline()