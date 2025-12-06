from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class BrowserService:
    """
    Responsibility: reliable browser instantiation and configuration.
    """
    @staticmethod
    def create_driver():
        try:
            print("[BrowserService] Initializing Optimized Headless Driver...")
            chrome_options = Options()
            
            # --- CONFIGURATION ---
            chrome_options.add_argument("--headless=new") 
            chrome_options.page_load_strategy = 'eager'
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-gpu")
            
            # Block resource-heavy elements
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            prefs = {
                "profile.managed_default_content_settings.images": 2, 
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_setting_values.geolocation": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Anti-detection
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
            chrome_options.add_argument("--lang=pt-PT")

            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(5)
            
            # CDP Command to hide webdriver property
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            })
            
            print("[BrowserService] Driver initialized.")
            return driver
            
        except Exception as e:
            print(f"[BrowserService] Failed to initialize driver: {e}")
            raise