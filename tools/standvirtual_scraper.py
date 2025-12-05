import time
import re
import os
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup

class StandvirtualScraper:
    """
    Scrapes car listings from Standvirtual.com.
    
    PERFORMANCE OPTIMIZATION:
    - Uses 'eager' page loading.
    - Uses BeautifulSoup for instant data parsing.
    - Runs in HEADLESS mode (background).
    - FIX: Advanced Price Extraction (Traverses up from currency symbol).
    """
    BASE_URL = "https://www.standvirtual.com/carros"

    def __init__(self):
        self.driver = None
        self._setup_driver()

    def _setup_driver(self):
        try:
            if self.driver:
                try: self.driver.quit()
                except: pass
            
            print("[Scraper] Initializing Optimized Headless Driver...")
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

            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(5)
            
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            })
            print("[Scraper] Driver initialized.")
            
        except Exception as e:
            print(f"[Scraper] Failed to initialize driver: {e}")
            raise

    def search(self, brand="", model="", min_price=None, max_price=None, min_year=None):
        # 1. Navigation Logic
        url = self.BASE_URL
        if brand:
            clean_brand = brand.lower().replace(" ", "-")
            url += f"/{clean_brand}"
            if model:
                clean_model = model.lower().replace(" ", "-")
                url += f"/{clean_model}"
        
        params = {}
        if min_price: params["search[filter_float_price:from]"] = min_price
        if max_price: params["search[filter_float_price:to]"] = max_price
        if min_year: params["search[filter_float_year:from]"] = min_year
        
        if params: url += f"?{urlencode(params)}"
            
        print(f"[Scraper] Navigating to: {url}")
        
        try:
            self.driver.get(url)
        except Exception:
            print("[Scraper] Connection issue, restarting driver...")
            self._setup_driver()
            self.driver.get(url)

        # 2. Fast Cookie Acceptance
        try:
            consent_button = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            consent_button.click()
        except:
            pass

        # 3. Wait for Content
        print("[Scraper] Waiting for page content...")
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
        except:
            if "Nenhum resultado" in self.driver.page_source:
                return []

        # 4. INSTANT EXTRACTION (BeautifulSoup)
        print("[Scraper] Parsing HTML...")
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        results = []
        articles = soup.find_all("article")
        
        print(f"[Scraper] Found {len(articles)} items. Processing...")

        for article in articles[:40]: 
            try:
                # --- A. Link & Title ---
                link_tag = article.find("a", href=True)
                if not link_tag: continue
                
                link = link_tag['href']
                
                # Title strategy
                title = "No Title"
                heading = article.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if heading:
                    title = heading.get_text(strip=True)
                elif link_tag.get_text(strip=True):
                    title = link_tag.get_text(strip=True)
                
                if "standvirtual.com" not in link: continue

                # --- B. Image ---
                image_url = ""
                img = article.find("img")
                if img:
                    image_url = img.get("src") or img.get("data-src") or ""

                # --- C. Price (TARGETED EXTRACTION) ---
                price = 0
                
                # Method 1: Look for specific price attribute
                price_elem = article.find(attrs={"data-testid": "ad-price"})
                if price_elem:
                    raw = price_elem.get_text(strip=True)
                    clean = re.sub(r'[^\d]', '', raw)
                    if clean: price = int(clean)

                # Method 2: Find the currency symbol and look at its neighbors
                if price == 0:
                    # Find text node with EUR or €
                    currency = article.find(string=re.compile(r'EUR|€', re.IGNORECASE))
                    if currency:
                        # Look at the parent element text (e.g. parent of <small>EUR</small> is <h3>29 900 <small>...)
                        container_text = currency.parent.parent.get_text(" ", strip=True)
                        # Regex: Look for numbers immediately before EUR/€
                        # Allows spaces, dots, commas, hyphens
                        match = re.search(r'([\d\s\.,-]+)\s*(?:EUR|€)', container_text, re.IGNORECASE)
                        if match:
                            clean = re.sub(r'[^\d]', '', match.group(1))
                            if clean: price = int(clean)
                
                # Method 3: Brute force regex on whole card
                if price == 0:
                    card_text = article.get_text(" ", strip=True)
                    match = re.search(r'([\d\s\.,]+)\s*(?:EUR|€)', card_text, re.IGNORECASE)
                    if match:
                         clean = re.sub(r'[^\d]', '', match.group(1))
                         if clean: price = int(clean)

                # Sanity Check
                if price < 500 or price > 10000000:
                    price = 0

                # --- D. Specs ---
                text_content = article.get_text(" ", strip=True)
                text_lower = text_content.lower()
                
                year = 0
                year_match = re.search(r'\b(19|20)\d{2}\b', text_lower)
                if year_match: year = int(year_match.group(0))

                km = 0
                km_match = re.search(r'(\d[\d\s\.]*)\s?km', text_lower)
                if km_match: 
                    clean_km = re.sub(r'[^\d]', '', km_match.group(1))
                    if clean_km: km = int(clean_km)

                fuel = "Other"
                if "gasolina" in text_lower: fuel = "Gasolina"
                elif "diesel" in text_lower: fuel = "Diesel"
                elif "elétrico" in text_lower: fuel = "Elétrico"
                elif "híbrido" in text_lower: fuel = "Híbrido"

                # --- VALIDATION ---
                if price == 0 and year == 0: continue

                results.append({
                    "title": title,
                    "price": price,
                    "year": year,
                    "km": km,
                    "fuel": fuel,
                    "link": link,
                    "image_url": image_url
                })
            except Exception:
                continue

        print(f"[Scraper] Done. Extracted {len(results)} valid cars.")
        return results

    def __del__(self):
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
        except:
            pass