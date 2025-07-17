import streamlit as st
import xgboost as xgb
from PIL import Image
from io import BytesIO
import base64
import webScrape.test as t

def init():
    model = xgb.XGBClassifier()
    model.load_model('model/CtfPd_model.json')
    return model

    # data = [50.00, 5, 2, 25]
    # data = np.array([data])

    # proba = model.predict_proba(data)
    # print("Probability of counterfeit:", proba[0][1])


def gui():
    st.title("Lazada Scraper via Backend")
    url = st.text_input("Enter Lazada product URL:")

    if st.button("Scrape"):
        if url:
            with st.spinner("Scraping..."):
                data = t.scrape_product_info(url)
                screenshot_data = base64.b64decode(data["screenshot"])
                screenshot = BytesIO(screenshot_data)
                st.image(screenshot, caption="Lazada Screenshot")
                st.write("**Title:**", data.get("title"))
                st.write("**Price:**", data.get("price"))
                


gui()