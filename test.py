import pandas as pd
import numpy as np

df = pd.read_csv('data\shopee_reviews.csv')
df.replace('', np.nan, inplace=True)
total_nulls = df.isnull().sum().sum()
print("Total null values:", total_nulls)
rows_with_nulls = df[df.isnull().any(axis=1)]
print(rows_with_nulls)
df = df.dropna()
total_nulls = df.isnull().sum().sum()
print("Total null values:", total_nulls)
