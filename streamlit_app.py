import streamlit as st
import xgboost as xgb
import requests
from PIL import Image
from io import BytesIO
import base64

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
                response = requests.post(
                    "http://localhost:5000/scrape",
                    json={"url": url}
                )
                data = response.json()

            if "error" in data:
                st.error(f"Error: {data['error']}")
            else:
                image_data = base64.b64decode(data["screenshot"])
                image = Image.open(BytesIO(image_data))
                st.image(image, caption="Screenshot", use_container_width=True)
                st.write("**Title:**", data.get("title"))
                st.write("**Price:**", data.get("price"))

gui()