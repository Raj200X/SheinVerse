import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

URL = "https://www.sheinindia.in/shein-shein-sleeveless-self-design-slitted-bodycon-dress/p/443385554_brown?user=old"

def debug_check():
    options = uc.ChromeOptions()
    options.add_argument("--no-first-run")
    options.add_argument("--no-service-autorun")
    options.add_argument("--password-store=basic")
    driver = uc.Chrome(options=options)
    
    print(f"Checking: {URL} ...")
    driver.get(URL)
    time.sleep(10) # Wait for full load
    
    page_source = driver.page_source.lower()
    
    stock_phrases = ["out of stock", "sold out", "notify me", "coming soon"]
    found_phrases = [phrase for phrase in stock_phrases if phrase in page_source]
    
    if found_phrases:
        print(f"FAIL: The script thinks this is OUT OF STOCK because it found these phrases:")
        for p in found_phrases:
            print(f" - '{p}'")
            
        # Optional: Save page source to file for inspection
        with open("debug_page.html", "w") as f:
            f.write(driver.page_source)
        print("Saved page source to debug_page.html")
    else:
        print("SUCCESS: The script correctly thinks this is IN STOCK.")

    driver.quit()

if __name__ == "__main__":
    debug_check()
