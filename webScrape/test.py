from playwright.sync_api import sync_playwright
import base64

BROWSERLESS_TOKEN = "2SgxintGKYQq7fS0e9cbecda5e203d0695049b406239675f1" 

def scrape_product_info(url):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"wss://production-sfo.browserless.io?token={BROWSERLESS_TOKEN}")
        try:
            # Safely get or create context
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.new_page()

            page.goto(url, timeout=60000)
            page.wait_for_load_state("domcontentloaded")

            # Wait for selectors to ensure elements are present
            page.wait_for_selector("h1.pdp-mod-product-badge-title", timeout=15000)
            page.wait_for_selector(".pdp-price_type_normal", timeout=15000)

            # Use locators
            title_element = page.locator("h1.pdp-mod-product-badge-title").first
            price_element = page.locator(".pdp-price_type_normal").first

            title = title_element.inner_text()
            price = price_element.inner_text()

            # Screenshot in base64
            screenshot_bytes = page.screenshot(full_page=True)
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")

            result = {
                "title": title,
                "price": price,
                "screenshot": screenshot_base64
            }

        except Exception as e:
            result = {"error": str(e)}
        
        finally:
            browser.close()
        
        return result
    

if __name__ == "__main__":
    data = scrape_product_info("https://www.lazada.com.my/products/alpine-strap-for-apple-watch-42-45-49mm-ocean-alpine-strap-bracelet-for-ultra-smart-watch-series-8-i3766312668-s21395667240.html?pvid=f322e92e-b624-4a7a-a16f-f92fe77c4b73&search=jfy&scm=1007.17519.386432.0&priceCompare=skuId%3A21395667240%3Bsource%3Atpp-recommend-plugin-32104%3Bsn%3Af322e92e-b624-4a7a-a16f-f92fe77c4b73%3BoriginPrice%3A319%3BdisplayPrice%3A319%3BsinglePromotionId%3A-1%3BsingleToolCode%3AmockedSalePrice%3BvoucherPricePlugin%3A0%3Btimestamp%3A1752738472329&spm=a2o4k.homepage.just4u.d_3766312668")
    print(data.get("title"))
    print(data.get("price"))