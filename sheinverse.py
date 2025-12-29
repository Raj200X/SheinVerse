import time
import os
import requests
import re
import platform
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# --- TELEGRAM CONFIGURATION ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8558911960:AAGeJmulVvTMY2DF1gU20_Icd1G_HxEo9Lk") 
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1028205933")
# ------------------------------

URL = "https://www.sheinindia.in/c/sverse-5939-37961"

from flask import Flask
import threading
from pyvirtualdisplay import Display # Import virtual display

app = Flask(__name__)

@app.route('/')
def health_check():
    return "SheinVerse Monitor is Running! 🚀"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
# -------------------------------------------

def get_driver():
    try:
        options = uc.ChromeOptions()
        options.add_argument("--no-first-run")
        options.add_argument("--no-service-autorun")
        options.add_argument("--password-store=basic")
        
        # HEADLESS MODIFICATION:
        # We NO LONGER use --headless=new because it gets detected.
        # Instead, we use Xvfb (via pyvirtualdisplay) to simulate a screen.
        # This makes Chrome think it has a GUI.
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.page_load_strategy = 'eager' # Don't wait for full page load (images, etc)
        
        # Use undetected-chromedriver
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(60) # Fail if page takes > 60s
        return driver
    except Exception as e:
        print(f"Failed to initialize driver: {e}")
        return None

def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, data=data)
        print("  -> Telegram alert sent!")
    except Exception as e:
        print(f"  -> Failed to send Telegram alert: {e}")

def check_stock_count():
    print("Initializing SheinVerse Monitor...")
    
    # Start Virtual Display (Xvfb) for Render
    if os.getenv("RENDER") or os.getenv("HEADLESS"):
        print("Starting Virtual Display (Xvfb)...")
        display = Display(visible=0, size=(1920, 1080))
        display.start()
    
    driver = None
    last_count = None
    
    while True:
        try:
            if driver is None:
                print("Launching browser...")
                driver = get_driver()
                if driver is None:
                    print("  -> Driver init failed. Retrying in 10s...")
                    time.sleep(10)
                    continue
                print("Browser initialized.")
            
            print(f"Checking SheinVerse...")
            try:
                driver.get(URL)
                
                # Check for redirections (Onelink, Deep links, etc.)
                time.sleep(10) # Wait for redirects and dynamic content
                current_url = driver.current_url
                page_source = driver.page_source.lower()

                # Handle deep_link_value wrapper page (copied from monitor.py)
                import urllib.parse
                if "deep_link_value" in current_url:
                    try:
                        parsed = urllib.parse.urlparse(current_url)
                        qs = urllib.parse.parse_qs(parsed.query)
                        if 'deep_link_value' in qs:
                            real_url = qs['deep_link_value'][0]
                            print(f"  -> Found deep link! Redirecting to real product page...")
                            driver.get(real_url)
                            time.sleep(10) # Wait longer for second load
                            page_source = driver.page_source.lower()
                    except Exception as e:
                        print(f"  -> Failed to parse deep link: {e}")

                # Get page text to find the count
                page_text = driver.find_element(By.TAG_NAME, "body").text
                
                # Regex to find "14 items found" or "X items found"
                # Case insensitive, handles potentially extra spaces.
                match = re.search(r'(\d+)\s+items\s+found', page_text, re.IGNORECASE)
                
                if match:
                    current_count = int(match.group(1))
                    print(f"  -> Found count: {current_count}")
                    
                    if last_count is None:
                        last_count = current_count
                        print(f"  -> Baseline set to {last_count}")
                    elif current_count > last_count:
                        print(f"  -> COUNT INCREASED! ({last_count} -> {current_count})")
                        msg = f"🚀 SHEINVERSE UPDATE 🚀\n\nNew products added!\nCount increased from {last_count} to {current_count}.\nLink: {URL}"
                        send_telegram_alert(msg)
                        last_count = current_count
                    elif current_count < last_count:
                        print(f"  -> Count decreased ({last_count} -> {current_count}). Updating baseline.")
                        last_count = current_count
                    else:
                        print("  -> No change.")
                else:
                    print("  -> [WARNING] Could not find 'items found' text on page.")
                    print(f"     Title: {driver.title}")
                    print(f"     URL: {driver.current_url}")
                    
                    # Check for bot detection
                    if "access denied" in page_text.lower() or "robot" in page_text.lower():
                        print("     [ALERT] Access Denied / Bot Detection triggered!")
                    
                    # Debug: print snippet
                    print(f"     Body snippet: {page_text[:500]}...")  
                    
                    # Search specifically for number patterns around 'items'
                    fallback_match = re.search(r'items', page_text, re.IGNORECASE)
                    if fallback_match:
                         start = max(0, fallback_match.start() - 50)
                         end = min(len(page_text), fallback_match.end() + 50)
                         print(f"     Context found: '...{page_text[start:end]}...'")

            except Exception as e:
                print(f"Error within check loop: {e}")
                # Check for browser crash/closure
                if "no such window" in str(e) or "invalid session" in str(e) or "web view not found" in str(e):
                    raise e # Re-raise to trigger outer loop restart

            # User requested 1 second interval, BUT to be safe we use 5 seconds to avoid IP ban.
            # 1 second is extremely risky for web scraping.
            time.sleep(5) 
            
        except Exception as e:
            print(f"Main loop error (browser restart needed): {e}")
            # traceback.print_exc() # Print full stack trace for debugging
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            driver = None
            time.sleep(5)

# --- IMPORT FLASK FOR RENDER WEB SERVICE ---
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def health_check():
    return "SheinVerse Monitor is Running! 🚀"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
# -------------------------------------------

if __name__ == "__main__":
    # Start the dummy web server in a background thread
    # This keeps Render happy (it needs a bound port)
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Run the main monitor loop
    check_stock_count()
