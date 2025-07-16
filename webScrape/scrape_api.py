from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
import os

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data.get("url")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        driver.set_window_size(1920, 1080)
        wait = WebDriverWait(driver, 10)

        price_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "pdp-price_type_normal"))
        )
        title_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "pdp-mod-product-badge-title"))
        )
        screenshot_bytes = driver.get_screenshot_as_png()
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')

        result = {
            "title": title_element.text,
            "price": price_element.text,
            "screenshot": screenshot_base64
        }

    except Exception as e:
        result = {"error": str(e)}

    finally:
        driver.quit()

    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
