from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
import json
import time
import random
import undetected_chromedriver as uc


def scrape_product_info(url):
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    service = Service("webScrape\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
            })
        """
    })

    try:
        driver.get(url)
        driver.set_window_size(1920, 1080)
        wait = WebDriverWait(driver, 10)
        screenshot_bytes = driver.get_screenshot_as_png()
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(1, 2))
        price_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "pdp-price_type_normal"))
        )
        title_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "pdp-mod-product-badge-title"))
        )
        seller_rating_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "rating-positive"))
        )
        total_purchase_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "pdp-review-summary__link"))
        )

        seller_rating = seller_rating_element.text.replace("%","")
        percentage = int(seller_rating)
        rating = 1.0 + (percentage / 100) * 4.0
        seller_rating = round(rating, 1)
        total_purchase = total_purchase_element.text.replace("Ratings ", "")

        result = {
            "title": title_element.text,
            "price": price_element.text.replace("RM",""),
            "screenshot": screenshot_base64,
            "seller_rating": seller_rating,
            "total_purchase": total_purchase
        }

    except Exception as e:
        result = {"error": str(e)}

    finally:
        driver.quit()

    return result

if __name__ == "__main__":
    data = scrape_product_info("https://www.lazada.com.my/products/menbense-mens-wallet-wax-oil-pu-leather-wallets-classic-fashion-purse-with-coin-pocket-retro-zipper-wallets-large-capacity-korean-style-mans-bag-business-multi-card-holder-dompet-lelaki-dompet-kulit-pu-i3893760583-s22841752333.html?pvid=3963c4af-7786-40c4-af6b-dc61966af4f3&search=jfy&scm=1007.17519.386432.0&priceCompare=skuId%3A22841752333%3Bsource%3Atpp-recommend-plugin-32104%3Bsn%3A3963c4af-7786-40c4-af6b-dc61966af4f3%3BoriginPrice%3A390%3BdisplayPrice%3A390%3BsinglePromotionId%3A-1%3BsingleToolCode%3AmockedSalePrice%3BvoucherPricePlugin%3A0%3Btimestamp%3A1752743816865&spm=a2o4k.homepage.just4u.d_3893760583")
    print("Title:", data['title'])
    print("Price:", data['price'])
    print("seller_rating:", data['seller_rating'])
    print("total_purchase:", data['total_purchase'])