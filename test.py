import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from scipy.sparse import hstack

df = pd.read_csv('data\shopee_reviews.csv')
df.replace('', np.nan, inplace=True)
df['label'] = pd.to_numeric(df['label'], errors='coerce')

# clean data
df = df.dropna()

# tf-idf
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['text'])

# k means clustering
ratings_scaled = MinMaxScaler().fit_transform(df[['label']])
ratings_sparse = np.array(ratings_scaled)
X_combined = hstack([tfidf_matrix, ratings_sparse])

k = 10
kmeans = KMeans(n_clusters=k, random_state=42)
kmeans.fit(X_combined)
df['cluster'] = kmeans.labels_


terms = vectorizer.get_feature_names_out()
order_centroids = kmeans.cluster_centers_[:, :len(terms)].argsort()[:, ::-1]

for i in range(k):
    top_terms = [terms[ind] for ind in order_centroids[i, :10]]
    print(f"Cluster {i} top terms: {', '.join(top_terms)}")

print(df)

print(df.groupby('cluster')['label'].mean())
print(df.groupby('cluster')['label'].value_counts(normalize=True))
