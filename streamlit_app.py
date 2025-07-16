import joblib
import numpy as np
import streamlit as st
import subprocess
import xgboost as xgb

def init():
    model = xgb.XGBClassifier()
    model.load_model('model/CtfPd_model.json')
    return model

    # data = [50.00, 5, 2, 25]
    # data = np.array([data])

    # proba = model.predict_proba(data)
    # print("Probability of counterfeit:", proba[0][1])


def gui():
    st.set_page_config(page_title="hello", layout="centered")
    st.title("Counterfeit Product Detector")

    model = init()

    st.write("Enter product details:")
    price = st.number_input("Price", min_value=0.0)
    rating = st.number_input("Seller Rating", min_value=0.0, max_value=5.0)
    reviews = st.number_input("Seller Reviews", min_value=0)
    shipping = st.number_input("Shipping Time (days)", min_value=0)

    if st.button("Predict"):
        data = np.array([[price, rating, reviews, shipping]])
        proba = model.predict_proba(data)
        prediction = model.predict(data)[0]

        st.write(f"Prediction: {'Counterfeit' if prediction == 1 else 'Genuine'}")
        st.write(f"Probability of being counterfeit: {proba[0][1]:.4f}")

gui()