import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
import time
import os

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def _parse_price(text):
    if not text:
        return None
    clean = str(text).replace("$", "").replace("€", "").replace(",", ".").strip()
    try:
        return float(clean)
    except ValueError:
        return None

def scrape_instant_gaming(pages=3):
    scrape_time = datetime.now().isoformat()
    rows = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "nl-NL,nl;q=0.9",
        "Referer": "https://www.instant-gaming.com/nl/",
        "X-Requested-With": "XMLHttpRequest",
    }
    for page in range(1, pages + 1):
        url = f"https://www.instant-gaming.com/nl/zoek/?type[]=steam&platform[]=1&orderby=discount&json=1&page={page}"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            data = response.json()
            hits = data.get("hits", [])
            for game in hits:
                rows.append({
                    "game_name": game.get("name", game.get("fullname", "Onbekend")),
                    "platform": game.get("platform", "PC"),
                    "price": _parse_price(game.get("price", game.get("min_price"))),
                    "discount": int(game.get("discount", 0) or 0),
                    "scraped_at": scrape_time,
                })
        except Exception as e:
            print(f"Fout pagina {page}: {e}")
        time.sleep(1)
    print(f"Klaar! {len(rows)} games gescrapt")
    return rows

def main():
    data = scrape_instant_gaming(pages=3)
    if data:
        supabase.table("instant_gaming_deals").insert(data).execute()
        print(f"Opgeslagen: {len(data)} rijen")

if __name__ == "__main__":
    main()
