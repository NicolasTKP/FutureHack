from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
import time
import random
import undetected_chromedriver as uc


def scrape_product_info(url):
    options = uc.ChromeOptions()
    # options.add_argument("--headless")
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
        driver.execute_script("window.scrollTo(0, 0);")
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
        
        reviews = []
        ratings =[]
        has_image=[]

        try:
            review_elements = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "item"))
            )
            for review in review_elements:
                try:
                    content = review.find_element(By.CLASS_NAME, "content").text
                    reviews.append(content)
                    stars = review.find_elements(By.CLASS_NAME, "star")
                    rating = 0
                    for star in stars:
                        if star.get_attribute("src") == "https://img.lazcdn.com/g/tps/tfs/TB19ZvEgfDH8KJjy1XcXXcpdXXa-64-64.png":
                            rating += 1
                    ratings.append(rating)
                    try:
                        image = review.find_element(By.CLASS_NAME, "review-image")
                        has_image.append(True)
                    except:
                        has_image.append(False)
                except:
                    print("Content not found in review.")
        except:
            print("Content not found in review.")

        screenshot_bytes = driver.get_screenshot_as_png()
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # while True:
            
        #     next_button_elements = wait.until(
        #         EC.presence_of_all_elements_located((By.CLASS_NAME, "next-btn"))
        #     )
            
        #     if len(next_button_elements) > 0:
        #         review_elements = wait.until(
        #             EC.presence_of_all_elements_located((By.CLASS_NAME, "item"))
        #         )
                
        #         for review in review_elements:
        #             try:
        #                 content = review.find_element(By.CLASS_NAME, "content").text
        #                 print(content)
        #                 rating = len(review.find_elements(By.CLASS_NAME, "star"))
        #                 print(rating)
        #             except:
        #                 print("Content not found in review.")
                
        #         old_reviews = driver.find_elements(By.CLASS_NAME, "item")
        #         next_button_elements[-1].click()
        #         wait.until(lambda d: len(d.find_elements(By.CLASS_NAME, "item")) != len(old_reviews))



        #     else:
        #         review_elements = wait.until(
        #             EC.presence_of_all_elements_located((By.CLASS_NAME, "item"))
        #         )
                
        #         for review in review_elements:
        #             try:
        #                 content = review.find_element(By.CLASS_NAME, "content").text
        #                 print(content)
        #                 rating = len(review.find_elements(By.CLASS_NAME, "star"))
        #                 print(content)
        #             except:
        #                 print("Content not found in review.")
                
        #         break

        result = {
            "title": title_element.text,
            "price": price_element.text.replace("RM",""),
            "screenshot": screenshot_base64,
            "seller_rating": seller_rating,
            "total_purchase": total_purchase,
            "reviews": reviews,
            "ratings":ratings,
            "has_image":has_image
        }

    except Exception as e:
        result = {"error": str(e)}

    finally:
        driver.quit()

    return result

if __name__ == "__main__":
    data = scrape_product_info("https://www.lazada.com.my/products/kegllect-men-quartz-watch-business-fashion-leather-strap-watches-for-men-jam-tangan-i3493058585-s19216981036.html?pvid=42557b30-1de8-4192-a887-7818f0ad404b&search=jfy&scm=1007.17519.386432.0&priceCompare=skuId%3A19216981036%3Bsource%3Atpp-recommend-plugin-32104%3Bsn%3A42557b30-1de8-4192-a887-7818f0ad404b%3BoriginPrice%3A567%3BdisplayPrice%3A567%3BsinglePromotionId%3A900000045296103%3BsingleToolCode%3ApromPrice%3BvoucherPricePlugin%3A0%3Btimestamp%3A1752763094920&spm=a2o4k.homepage.just4u.d_3493058585")
    print("Title:", data['title'])
    print("Price:", data['price'])
    print("seller_rating:", data['seller_rating'])
    print("total_purchase:", data['total_purchase'])

    for review in data["reviews"]:
        print(review)