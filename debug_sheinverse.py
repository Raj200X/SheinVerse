import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

URL = "https://www.sheinindia.in/c/sverse-5939-37961"

def debug_check():
    options = uc.ChromeOptions()
    options.add_argument("--no-first-run")
    options.add_argument("--no-service-autorun")
    options.add_argument("--password-store=basic")
    driver = uc.Chrome(options=options)
    
    print(f"Checking: {URL} ...")
    driver.get(URL)
    time.sleep(15) # Wait for full load and dynamic content
    
    page_source = driver.page_source.lower()
    
    # Save source for manual inspection if needed
    with open("debug_sverse.html", "w") as f:
        f.write(driver.page_source)
    print("Saved page source to debug_sverse.html")
    
    # Try to find the "items found" text
    try:
        # Search for typical patterns
        body_text = driver.find_element(By.TAG_NAME, "body").text
        print("\n--- BODY TEXT SNIPPET ---")
        print(body_text[:1000]) # Print first 1000 chars
        
        if "items found" in page_source:
             print("\n[SUCCESS] Found 'items found' in page source.")
        else:
             print("\n[WARNING] Did NOT find 'items found' in page source.")
             
    except Exception as e:
        print(f"Error inspecting page: {e}")

    driver.quit()

if __name__ == "__main__":
    debug_check()
