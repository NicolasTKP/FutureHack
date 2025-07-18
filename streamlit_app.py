import streamlit as st
import xgboost as xgb
import base64
import webScrape.scraper as scraper
import numpy as np
import joblib
import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
import pandas as pd
nltk.download('stopwords')
nltk.download('vader_lexicon')
from scipy.sparse import hstack
from sklearn.metrics.pairwise import cosine_similarity

malicious_words = set([
    "cheating","fuck","terrible","brainless","hell","sb","stupid","idiot","useless","sucks","garbage","trash","fool","hate", "dumbass", "nonsense","fake","ass",
    "tipu","skam","jangan beli","bodoh","sial","penipu","palse","babi","teruk", "tak guna", "sampah", "celaka"
])
sia = SentimentIntensityAnalyzer()
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

def compute_cosine_similarities(df, threshold=0.85):
    if df.empty:
        return []
    ctfpdModel, bgdModel, bgdm_vectorizer, smModel, sm_vectorizer = init()
    tfidf_matrix = sm_vectorizer.transform(df['clean_text'])
    similarity_matrix = cosine_similarity(tfidf_matrix)

    similar_pairs = []
    num_reviews = df.shape[0]

    for i in range(num_reviews):
        for j in range(i + 1, num_reviews):
            similarity_score = similarity_matrix[i, j]
            if similarity_score > threshold:
                similar_pairs.append({
                    "review_1": df['review'].iloc[i],
                    "review_2": df['review'].iloc[j],
                    "similarity_score": similarity_score
                })

    return similar_pairs

def contains_malicious(text, word_set):
    matched_words = [word for word in word_set if re.search(rf'\b{re.escape(word)}\b', text, re.IGNORECASE)]
    return bool(matched_words), matched_words

def gui():
    ctfpdModel, bgdModel, bgdm_vectorizer, smModel, sm_vectorizer = init()
    st.title("Lazada Veracity Checker")
    url = st.text_input("Enter Lazada product URL:")

    if st.button("Scrape"):
        if url:
            with st.spinner("Scraping..."):
                data = scraper.scrape_product_info(url)

                # Product Details
                if 'screenshot' in data and data['screenshot'] is not None:
                    screenshot_data = base64.b64decode(data['screenshot'])
                    st.image(screenshot_data, caption="Product", use_container_width=True)
                else:
                    st.warning("Screenshot not available.")

                st.write("**Product Name:**", data['title'])
                st.write("**Price:**", data['price'])
                st.write("**Total Purchase:**", data["total_purchase"])
                st.write("**Seller Ratings:**", data['seller_rating'])

                X = [float(data["price"].replace(",", "")), float(data["total_purchase"]), int(data["seller_rating"])]
                X = np.array([X])
                
                # Counterfeit detection
                proba = ctfpdModel.predict_proba(X)
                if proba[0][1] > 0.8: #threshold for counterfeit detection
                    st.write("")
                    st.write("⚠️ This product is likely counterfeit.")
                    st.write("**Probability of counterfeit:**", round(proba[0][1] * 100, 2), "%")

                st.write("")
                st.markdown(
                    "<h1 style='text-align: center;'>Customer Reviews</h1>",
                    unsafe_allow_html=True
                )
                st.write("---")

                # ratings
                for i in range(len(data["reviews"])):
                    with st.expander("Review {}".format(i+1)):
                        st.write("**Rating:**",data["ratings"][i])
                        st.write("**Has Image:**",data["has_image"][i])
                        st.write("**Date:**",data["dates"][i])
                        st.write("**Review:**",data["reviews"][i])

                    # Bot detection
                    new_reviews = [
                        {'text_': data["reviews"][i], 'rating': int(data["ratings"][i])},
                    ]
                    new_df = pd.DataFrame(new_reviews)
                    
                    new_df['clean_text'] = new_df['text_'].apply(clean_text)
                    new_df['review_length'] = new_df['clean_text'].apply(lambda x: len(x.split()))
                    X_tfidf_new = bgdm_vectorizer.transform(new_df['clean_text'])
                    X_other_new = new_df[['review_length', 'rating']].astype(float).values
                    X_new = hstack([X_tfidf_new, X_other_new])

                    proba = bgdModel.predict_proba(X_new)[:, 0]
                    if proba[0] > 0.7: #threshold for bot detection
                        st.write("")
                        st.write("⚠️ This review is likely bot generated.")
                        st.write("**Probability of bot generated:**", round(proba[0] * 100, 2), "%")


                    # Sentiment Detection
                    new_review = {
                        'review': data["reviews"][i]
                    }
                    new_df = pd.DataFrame([new_review])
                    new_df['clean_text'] = new_df['review'].apply(clean_text)
                    new_df['review_length'] = new_df['clean_text'].apply(lambda x: len(x.split()))
                    new_df['vader_score'] = new_df['review'].apply(lambda x: sia.polarity_scores(x)['compound'])

                    X_tfidf_new = sm_vectorizer.transform(new_df['clean_text'])
                    X_other_new = new_df[['review_length', 'vader_score']].astype(float).values
                    X_new = hstack([X_tfidf_new, X_other_new])

                    pred_label = smModel.predict(X_new)[0]
                    if int(data["ratings"][i]) >= 3:
                        sentiment = "positive"
                    else:
                        sentiment = "negative"
                    
                    if pred_label != sentiment:
                        st.write("")
                        st.write("⚠️ There might be a mismatch of sentiment between rating and review.")
                        st.write("**Rating Sentiment:**", sentiment)
                        st.write("**Review Sentiment:**", pred_label)

                    # Malicious word detection
                    for index, row in new_df.iterrows():
                        isMalicious, matchWords = contains_malicious(row['clean_text'], malicious_words)

                        if isMalicious:
                            st.write("")
                            st.write("⚠️ There is a malicious word contained in this review.")
                            st.write("**Malicious words:**", matchWords)

                    st.write("---")

                #   consine similarity                
                review_df = pd.DataFrame({
                    'review': data["reviews"]
                })
                review_df['clean_text'] = review_df['review'].apply(clean_text)
                similar_pairs = compute_cosine_similarities(review_df, threshold=0.75)

                if similar_pairs:
                    st.markdown(
                        "<h1 style='text-align: center;'>Suspicious Reviews with High Similarity</h1>",
                        unsafe_allow_html=True
                    )
                    for pair in similar_pairs:
                        st.write(f"**Similarity Score:** {pair['similarity_score']:.2f}")
                        st.write(f"• Review 1: {pair['review_1']}")
                        st.write(f"• Review 2: {pair['review_2']}")
                        st.write("---")
                
    
gui()