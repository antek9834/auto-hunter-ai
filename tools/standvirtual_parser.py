import re
from bs4 import BeautifulSoup

class StandvirtualParser:
    """
    Responsibility: Extracting clean data from raw HTML.
    """
    
    @staticmethod
    def parse_listing(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        articles = soup.find_all("article")
        
        print(f"[Parser] Found {len(articles)} items. Processing...")

        for article in articles[:40]: 
            try:
                data = StandvirtualParser._extract_single_article(article)
                if data:
                    results.append(data)
            except Exception:
                continue
        
        return results

    @staticmethod
    def _extract_single_article(article):
        # --- Link & Title ---
        link_tag = article.find("a", href=True)
        if not link_tag: return None
        
        link = link_tag['href']
        if "standvirtual.com" not in link: return None

        title = "No Title"
        heading = article.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if heading:
            title = heading.get_text(strip=True)
        elif link_tag.get_text(strip=True):
            title = link_tag.get_text(strip=True)

        # --- Image ---
        image_url = ""
        img = article.find("img")
        if img:
            image_url = img.get("src") or img.get("data-src") or ""

        # --- Price ---
        price = StandvirtualParser._extract_price(article)

        # --- Specs ---
        year, km, fuel = StandvirtualParser._extract_specs(article)

        # --- Validation ---
        if price == 0 and year == 0: return None

        return {
            "title": title,
            "price": price,
            "year": year,
            "km": km,
            "fuel": fuel,
            "link": link,
            "image_url": image_url
        }

    @staticmethod
    def _extract_price(article):
        price = 0
        
        # Method 1: Data Attribute
        price_elem = article.find(attrs={"data-testid": "ad-price"})
        if price_elem:
            raw = price_elem.get_text(strip=True)
            clean = re.sub(r'[^\d]', '', raw)
            if clean: price = int(clean)

        # Method 2: Currency Neighbor Search
        if price == 0:
            currency = article.find(string=re.compile(r'EUR|€', re.IGNORECASE))
            if currency:
                container_text = currency.parent.parent.get_text(" ", strip=True)
                match = re.search(r'([\d\s\.,-]+)\s*(?:EUR|€)', container_text, re.IGNORECASE)
                if match:
                    clean = re.sub(r'[^\d]', '', match.group(1))
                    if clean: price = int(clean)
        
        # Method 3: Brute Force
        if price == 0:
            card_text = article.get_text(" ", strip=True)
            match = re.search(r'([\d\s\.,]+)\s*(?:EUR|€)', card_text, re.IGNORECASE)
            if match:
                    clean = re.sub(r'[^\d]', '', match.group(1))
                    if clean: price = int(clean)
        
        # Sanity Check
        if price < 500 or price > 10000000: return 0
        return price

    @staticmethod
    def _extract_specs(article):
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
        
        return year, km, fuel