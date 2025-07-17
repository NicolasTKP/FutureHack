import streamlit as st
import xgboost as xgb
import base64
import webScrape.scraper as scraper
import numpy as np
import json

def init():
    model = xgb.XGBClassifier()
    model.load_model('model/CtfPd_model.json')
    return model

    # data = [50.00, 5, 2, 25]
    # data = np.array([data])

    # proba = model.predict_proba(data)
    # print("Probability of counterfeit:", proba[0][1])


def gui():
    model = init()
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
                proba = model.predict_proba(X)
                if proba[0][1] > 0.5:
                    st.write("⚠️ This review is likely counterfeit.")
                    st.write("**Probability of counterfeit:**", round(proba[0][1] * 100, 2), "%")
                else:
                    st.write("✅ This product seems genuine.")
                    st.write("**Probability of authenticity:**", round((1 - proba[0][1]) * 100, 2), "%")
                st.write("")
                st.write("")
                st.write("---")

                for i in range(len(data["reviews"])):
                    st.write("**Rating:**",data["ratings"][i])
                    st.write("**Has Image:**",data["has_image"][i])
                    st.write("**Review:**",data["reviews"][i])
                    st.write("---")

                
                

    

gui()