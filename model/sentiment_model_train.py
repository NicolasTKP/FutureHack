import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from imblearn.over_sampling import RandomOverSampler
from nltk.sentiment import SentimentIntensityAnalyzer
from scipy.sparse import hstack
nltk.download('vader_lexicon')
nltk.download('stopwords')

file_path = 'data\\review_sentiment.csv'
df = pd.read_csv(file_path)

"""Text preprocessing"""
stop_words = set(stopwords.words('english'))

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z\s]', '', text)  # remove punctuation/numbers
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

df['expected_sentiment'] = df['expected_sentiment'].replace('neutral', 'positive')
df['clean_text'] = df['review'].apply(clean_text)

"""Feature engineering"""
sia = SentimentIntensityAnalyzer()
df['review_length'] = df['clean_text'].apply(lambda x: len(x.split()))
df['vader_score'] = df['review'].apply(lambda x: sia.polarity_scores(x)['compound'])

tfidf = TfidfVectorizer(ngram_range=(1,2), max_features=5000)

X_tfidf = tfidf.fit_transform(df['clean_text'])
X_other = df[['review_length', 'vader_score']].astype(float).values
X = hstack([X_tfidf, X_other])

y = df['expected_sentiment'].values

print(df.columns)

"""Train/test split"""
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

ros = RandomOverSampler(random_state=42)

X_resampled, y_resampled = ros.fit_resample(X_train, y_train)
X_test_resampled, y_test_resampled = ros.fit_resample(X_test, y_test)

"""Build detection model"""
model = LinearSVC(class_weight='balanced')
model.fit(X_resampled, y_resampled)

y_pred = model.predict(X_test_resampled)

"""Evaluate model"""
print("Classification Report:\n", classification_report(y_test_resampled, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test_resampled, y_pred))



"""test1"""

new_review = {
    'review': "Just received.. haven't try."
}

new_df = pd.DataFrame([new_review])
new_df['clean_text'] = new_df['review'].apply(clean_text)
new_df['review_length'] = new_df['clean_text'].apply(lambda x: len(x.split()))
new_df['vader_score'] = new_df['review'].apply(lambda x: sia.polarity_scores(x)['compound'])

X_tfidf_new = tfidf.transform(new_df['clean_text'])
X_other_new = new_df[['review_length', 'vader_score']].astype(float).values
X_new = hstack([X_tfidf_new, X_other_new])

pred_label = model.predict(X_new)[0]
print("Text:", new_df['review'])
print("Detection:", pred_label)

"""Test2"""

new_review = {
    'review': "Great value. Delivered quickly. Would buy again."
}
new_df = pd.DataFrame([new_review])
new_df['clean_text'] = new_df['review'].apply(clean_text)
new_df['review_length'] = new_df['clean_text'].apply(lambda x: len(x.split()))
new_df['vader_score'] = new_df['review'].apply(lambda x: sia.polarity_scores(x)['compound'])

X_tfidf_new = tfidf.transform(new_df['clean_text'])
X_other_new = new_df[['review_length', 'vader_score']].astype(float).values
X_new = hstack([X_tfidf_new, X_other_new])

pred_label = model.predict(X_new)[0]
print("Text:", new_df['review'])
print("Detection:", pred_label)


#Save model
import joblib
joblib.dump(tfidf, 'model/sm_tfidf_vectorizer.pkl')
joblib.dump(model, 'model/Sentiment_Model.pkl')