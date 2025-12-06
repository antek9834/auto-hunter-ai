from urllib.parse import urlencode
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tools.standvirtual_parser import StandvirtualParser
from tools.browser_service import BrowserService

class StandvirtualScraper:
    """
    Orchestrates the scraping process using dedicated services.
    """
    BASE_URL = "https://www.standvirtual.com/carros"

    def __init__(self):
        self.driver = None
        # We don't init driver here immediately to save resources until needed, 
        # or we can do it now.
        self._restart_driver()

    def _restart_driver(self):
        if self.driver:
            try: self.driver.quit()
            except: pass
        self.driver = BrowserService.create_driver()

    def _build_url(self, brand, model, min_price, max_price, min_year):
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
        return url

    def search(self, brand="", model="", min_price=None, max_price=None, min_year=None):
        url = self._build_url(brand, model, min_price, max_price, min_year)
        print(f"[Scraper] Navigating to: {url}")
        
        try:
            self.driver.get(url)
        except Exception:
            print("[Scraper] Connection issue, restarting driver...")
            self._restart_driver()
            self.driver.get(url)

        # Cookie Acceptance
        try:
            consent_button = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            consent_button.click()
        except:
            pass

        # Wait for Content
        print("[Scraper] Waiting for page content...")
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
        except:
            if "Nenhum resultado" in self.driver.page_source:
                return []

        # DELEGATE PARSING
        print("[Scraper] Parsing HTML...")
        return StandvirtualParser.parse_listing(self.driver.page_source)

    def __del__(self):
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
        except:
            pass