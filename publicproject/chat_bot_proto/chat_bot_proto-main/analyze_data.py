import pandas as pd
import numpy as np

# Load and analyze sample_data.xlsx
df = pd.read_excel('sample_data.xlsx')

print("=== SAMPLE DATA ANALYSIS ===")
print(f"Columns: {df.columns.tolist()}")
print(f"Shape: {df.shape}")
print(f"Total rows: {len(df)}")

print("\n=== DATA TYPES ===")
print(df.dtypes)

print("\n=== BASIC STATISTICS ===")
print(df.describe(include='all'))

print("\n=== FIRST 5 ROWS ===")
print(df.head())

print("\n=== SAMPLE DATA FROM EACH COLUMN ===")
for col in df.columns:
    print(f"\n{col}:")
    print(f"  Unique values: {df[col].nunique()}")
    print(f"  Sample values: {df[col].dropna().head(3).tolist()}")
    if df[col].dtype == 'object':
        print(f"  Max length: {df[col].astype(str).str.len().max()}")

print("\n=== NULL VALUES ===")
print(df.isnull().sum())

print("\n=== UNIQUE VALUE COUNTS FOR CATEGORICAL COLUMNS ===")
for col in df.columns:
    if df[col].dtype == 'object' and df[col].nunique() < 20:
        print(f"\n{col} value counts:")
        print(df[col].value_counts().head(10))