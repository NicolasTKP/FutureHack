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
                try:
                    response = requests.post(
                        "https://futurehack.onrender.com/scrape",
                        json={"url": url},
                        timeout=100  # Optional timeout for safety
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if "error" in data:
                            st.error(f"Error: {data['error']}")
                        else:
                            image_data = base64.b64decode(data["screenshot"])
                            image = Image.open(BytesIO(image_data))
                            st.image(image, caption="Screenshot", use_container_width=True)
                            st.write("**Title:**", data.get("title"))
                            st.write("**Price:**", data.get("price"))
                    else:
                        st.error(f"Backend Error: {response.status_code}\n{response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Request failed: {str(e)}")

gui()