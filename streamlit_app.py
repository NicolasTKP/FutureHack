import streamlit as st
import xgboost as xgb
import base64
import webScrape.scraper as scraper
import numpy as np

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
    st.title("Lazada Scraper via Backend")
    url = st.text_input("Enter Lazada product URL:")

    if st.button("Scrape"):
        if url:
            with st.spinner("Scraping..."):
                data = scraper.scrape_product_info(url)
                if "screenshot" in data and data["screenshot"] is not None:
                    screenshot_data = base64.b64decode(data["screenshot"])
                    st.image(screenshot_data, caption="Screenshot", use_column_width=True)
                else:
                    st.warning("Screenshot not available.")
                st.write("**Product Name:**", data.get("title"))
                st.write("**Price:**", data.get("price"))
                st.write("**Total Purchase:**", data.get("total_purchase"))
                st.write("**Seller Ratings:**", data.get("seller_ratings"))
                X = [float(data.get("price")), float(data.get("seller_ratings")), int(data.get("total_purchase"))]
                X = np.array([X])
                proba = model.predict_proba(data)
                st.write("**Probability of counterfeit:**", proba[0][1])

    

gui()