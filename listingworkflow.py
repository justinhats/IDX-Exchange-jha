import pandas as pd

# load march 2026 listing data
df = pd.read_csv('CRMLSListing202603.csv', encoding='latin1')

# view first 5 rows
print("\n[Data Preview]:")
print(df.head())

# view column names to look at available fields
print("\n[Column Names]:")
print(df.columns.tolist())

# summary statistics for market pricing and metrics
print("\n[Statistical Summary]:")
print(df.describe())
