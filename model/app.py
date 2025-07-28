from flask import Flask, request, jsonify
import xgboost as xgb
import joblib
import pandas as pd
import re
import nltk
nltk.data.path.append('./model/nltk_data')
from nltk.corpus import stopwords
from scipy.sparse import hstack
import numpy as np
stop_words = set(stopwords.words('english'))

def init():
    ctfpdModel = xgb.XGBClassifier()
    ctfpdModel.load_model('model/CtfPd_model.json')

    bgdModel = joblib.load('model/Bot_Generated_Detection_Model.pkl')
    bgdm_vectorizer = joblib.load('model/bgdm_tfidf_vectorizer.pkl')

    smModel = joblib.load('model/Sentiment_Model.pkl')
    sm_vectorizer = joblib.load('model/sm_tfidf_vectorizer.pkl')

    return ctfpdModel, bgdModel, bgdm_vectorizer, smModel, sm_vectorizer

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z\s]', '', text)  # remove punctuation/numbers
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)


ctfpdModel, bgdModel, bgdm_vectorizer, smModel, sm_vectorizer = init()
app = Flask(__name__)

@app.route('/post/bg', methods=['POST'])
def bot_generate():
    data = request.get_json() 
    new_reviews = [{'review':data.get('review'), 'rating': int(data.get('rating'))}]
    new_df = pd.DataFrame(new_reviews)
    new_df['clean_text'] = new_df['review'].apply(clean_text)
    new_df['review_length'] = new_df['clean_text'].apply(lambda x: len(x.split()))
    X_tfidf_new = bgdm_vectorizer.transform(new_df['clean_text'])
    X_other_new = new_df[['review_length', 'rating']].astype(float).values
    X_new = hstack([X_tfidf_new, X_other_new])
    proba = bgdModel.predict_proba(X_new)[:, 0]

    if not new_reviews:
        return jsonify({"error": "review and rating is required"}), 400

    return jsonify({"proba": proba[0]})


@app.route('/post/cp', methods=['POST'])
def counterfeit_product():
    data = request.get_json() 
    new_product = [float(data.get('price')), float(data.get('total_purchase')),int(data.get('seller_rating'))]

    if not new_product:
        return jsonify({"error": "new_product is required"}), 400
    
    X = np.array([new_product])
    proba = ctfpdModel.predict_proba(X)

    return jsonify({"proba": float(proba[0][1])})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000) 

