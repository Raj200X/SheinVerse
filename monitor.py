import time
import os
import requests
import platform
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# --- TELEGRAM CONFIGURATION ---
# Replace these with your actual details
TELEGRAM_BOT_TOKEN = "8558911960:AAGeJmulVvTMY2DF1gU20_Icd1G_HxEo9Lk" 
TELEGRAM_CHAT_ID = "1028205933"
# ------------------------------

URLS = [
    "https://www.sheinindia.in/shein-shein-sleeveless-self-design-slitted-bodycon-dress/p/443385554_brown?user=old",
    "https://sheinindia.onelink.me/ZrSt/bi20lj6n",
    "https://sheinindia.onelink.me/ZrSt/lgikup3d",
    "https://sheinindia.onelink.me/ZrSt/6gjx0e31",
    "https://sheinindia.onelink.me/ZrSt/uwhkddow",
    "https://sheinindia.onelink.me/ZrSt/s5rxa60a",
    "https://sheinindia.onelink.me/ZrSt/c7dcljxi",
    "https://sheinindia.onelink.me/ZrSt/l7pk41bi",
    "https://sheinindia.onelink.me/ZrSt/dmij73m2",
    "https://sheinindia.onelink.me/ZrSt/h7qh39kh",
    "https://sheinindia.onelink.me/ZrSt/9p74086t"

]

def get_driver():
    options = uc.ChromeOptions()
    # options.add_argument("--headless=new") # Keep visible for now
    options.add_argument("--no-first-run")
    options.add_argument("--no-service-autorun")
    options.add_argument("--password-store=basic")
    
    # Use undetected-chromedriver
    # It automatically handles driver binary versioning and patches
    return uc.Chrome(options=options)

def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, data=data)
        print("  -> Telegram alert sent!")
    except Exception as e:
        print(f"  -> Failed to send Telegram alert: {e}")


def check_stock():
    print("Initializing stealth browser... (this may take a moment)")
    driver = None
    
    while True:
        try:
            if driver is None:
                driver = get_driver()
                print("Browser initialized.")
            
            for url in URLS:
                try:
                    print(f"Checking: {url} ...")
                    driver.get(url)
                    
                    # Wait for redirects and page load (5 seconds is usually enough for Onelink -> Shein)
                    time.sleep(8)
                    
                    # Get page text
                    page_source = driver.page_source.lower()
                    current_url = driver.current_url
                    
                    # Check if we are still on the redirect page (failed to redirect)
                    if "onelink.me" in current_url:
                        print(f"  -> Stuck on redirect: {current_url}")
                        continue
                        
                    # Check for access denied
                    if "access denied" in page_source:
                        print(f"  -> Access Denied (Bot detected)")
                        continue
                    
                    # Handle deep_link_value wrapper page
                    import urllib.parse
                    if "deep_link_value" in current_url:
                        try:
                            parsed = urllib.parse.urlparse(current_url)
                            qs = urllib.parse.parse_qs(parsed.query)
                            if 'deep_link_value' in qs:
                                real_url = qs['deep_link_value'][0]
                                print(f"  -> Found deep link! Redirecting to real product page...")
                                driver.get(real_url)
                                time.sleep(5)
                                page_source = driver.page_source.lower()
                                current_url = driver.current_url
                        except Exception as e:
                            print(f"  -> Failed to parse deep link: {e}")

                    # Stock checking logic
                    stock_phrases = ["out of stock", "sold out", "notify me"]
                    if any(phrase in page_source for phrase in stock_phrases):
                        print(f"  -> Out of stock")
                    else:
                        print(f"  -> STOCK AVAILABLE !!! ({current_url})")
                        
                        # Actions on stock found:
                        # 1. Open Browser
                        # import webbrowser
                        # webbrowser.open(current_url)
                        
                        # 2. Telegram Alert
                        alert_msg = f"🚨 SHEIN STOCK ALERT 🚨\n\nProduct is available!\nLink: {current_url}"
                        send_telegram_alert(alert_msg)
                        
                except Exception as e:
                    print(f"Error checking {url}: {e}")
                    # Check if error is due to closed window/session
                    if "no such window" in str(e) or "invalid session" in str(e) or "web view not found" in str(e):
                        print("Browser window closed or crashed. Restarting browser...")
                        try:
                            driver.quit()
                        except:
                            pass
                        driver = None
                        break # Break url loop to re-init driver
                
                time.sleep(3)

            print("Cycle completed. Waiting 45 seconds to avoid rate limits...")
            time.sleep(45)
            
        except KeyboardInterrupt:
            print("\nStopping monitor...")
            break
        except Exception as e:
            print(f"Main loop error: {e}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            driver = None
            time.sleep(5) # Wait before retry

    if driver:
        driver.quit()

if __name__ == "__main__":
    check_stock()
