import streamlit as st
import xgboost as xgb
import base64
import webScrape.scraper as scraper
import numpy as np
import joblib
import re
import nltk
from nltk.corpus import stopwords
import pandas as pd
nltk.download('stopwords')
from scipy.sparse import hstack

def init():
    ctfpdModel = xgb.XGBClassifier()
    ctfpdModel.load_model('model/CtfPd_model.json')

    bgdModel = joblib.load('model/Bot_Generated_Detection_Model.pkl')

    vectorizer = joblib.load('model/bgdm_tfidf_vectorizer.pkl')

    return ctfpdModel, bgdModel, vectorizer

    # data = [50.00, 5, 2, 25]
    # data = np.array([data])

    # proba = model.predict_proba(data)
    # print("Probability of counterfeit:", proba[0][1])

stop_words = set(stopwords.words('english'))
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z\s]', '', text)  # remove punctuation/numbers
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

def gui():
    ctfpdModel, bgdModel, vectorizer = init()
    st.title("Lazada Scraper")
    url = st.text_input("Enter Lazada product URL:")

    if st.button("Scrape"):
        if url:
            with st.spinner("Scraping..."):
                data = scraper.scrape_product_info(url)
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

                proba = ctfpdModel.predict_proba(X)
                if proba[0][1] > 0.8: #threshold for counterfeit detection
                    st.write("⚠️ This product is likely counterfeit.")
                    st.write("**Probability of counterfeit:**", round(proba[0][1] * 100, 2), "%")
                else:
                    st.write("✅ This product seems genuine.")
                    st.write("**Probability of authenticity:**", round((1 - proba[0][1]) * 100, 2), "%")

                st.write("")
                st.write("")
                st.markdown(
                    "<h1 style='text-align: center;'>Customer Reviews</h1>",
                    unsafe_allow_html=True
                )
                st.write("---")

                for i in range(len(data["reviews"])):
                    st.write("**Rating:**",data["ratings"][i])
                    st.write("**Has Image:**",data["has_image"][i])
                    st.write("**Review:**",data["reviews"][i])

                    new_reviews = [
                        {'text_': data["reviews"][i], 'rating': int(data["ratings"][i])},
                    ]
                    new_df = pd.DataFrame(new_reviews)
                    
                    new_df['clean_text'] = new_df['text_'].apply(clean_text)
                    new_df['review_length'] = new_df['clean_text'].apply(lambda x: len(x.split()))
                    X_tfidf_new = vectorizer.transform(new_df['clean_text'])
                    X_other_new = new_df[['review_length', 'rating']].astype(float).values
                    X_new = hstack([X_tfidf_new, X_other_new])

                    proba = bgdModel.predict_proba(X_new)[:, 0]
                    if proba[0] > 0.5: #threshold for bot detection
                        st.write("⚠️ This review is likely bot generated.")
                        st.write("**Probability of bot generated:**", round(proba[0] * 100, 2), "%")
                    else:
                        st.write("✅ This review seems genuine.")
                        st.write("**Probability of authenticity:**", round((1 - proba[0]) * 100, 2), "%")

                    st.write("---")

                
                

    

gui()