import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime
import csv
from typing import List

@dataclass
class Offer:
    source: str
    title: str
    price: int
    mileage: int
    year: int
    url: str
    country: str
    created_at: datetime


def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; FN2-Finder/1.0)"
    }
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.text


# ============================================================
#  BLOCKET – RSS (działa w GitHub Actions, brak 403)
# ============================================================

def parse_blocket_rss(max_price: int, max_mileage: int) -> List[Offer]:
    url = "https://www.blocket.se/annonser/hela_sverige/fordon/bilar.rss?q=Honda%20Civic%20Type%20R%20FN2"

    html = fetch_html(url)
    soup = BeautifulSoup(html, "xml")

    offers = []

    for item in soup.find_all("item"):
        title = item.title.text
        link = item.link.text

        if "FN2" not in title and "Type R" not in title:
            continue

        # Pobieramy cenę z HTML ogłoszenia
        try:
            offer_html = fetch_html(link)
            offer_soup = BeautifulSoup(offer_html, "html.parser")
            price_el = offer_soup.select_one(".price")
            if not price_el:
                continue
            price = int(price_el.get_text(strip=True).replace(" ", "").replace("kr", ""))
        except:
            continue

        if price > max_price:
            continue

        offers.append(
            Offer(
                source="blocket-rss",
                title=title,
                price=price,
                mileage=0,
                year=0,
                url=link,
                country="Sweden",
                created_at=datetime.utcnow()
            )
        )

    return offers


# ============================================================
#  WAYKE
# ============================================================

def parse_wayke_fn2(max_price: int, max_mileage: int) -> List[Offer]:
    url = "https://www.wayke.se/sok?q=Honda%20Civic%20Type%20R%20FN2"

    html = fetch_html(url)
    soup = BeautifulSoup(html, "lxml")

    offers = []

    for card in soup.select("a.vehicle-card"):
        title_el = card.select_one("h3")
        price_el = card.select_one(".price")
        mileage_el = card.select_one(".mileage")
        year_el = card.select_one(".year")

        if not (title_el and price_el):
            continue

        title = title_el.get_text(strip=True)
        if "Type R" not in title:
            continue

        url_offer = "https://www.wayke.se" + card["href"]

        price = int(price_el.get_text(strip=True).replace(" ", "").replace("kr", ""))
        if price > max_price:
            continue

        mileage_mil = 0
        if mileage_el:
            try:
                mileage_mil = int(mileage_el.get_text(strip=True).replace(" ", "").replace("mil", ""))
            except:
                mileage_mil = 0

        mileage_km = mileage_mil * 10
        if mileage_km > max_mileage:
            continue

        year = int(year_el.get_text(strip=True)) if year_el else 0

        offers.append(
            Offer("wayke", title, price, mileage_km, year, url_offer, "Sweden", datetime.utcnow())
        )

    return offers


# ============================================================
#  OTOMOTO
# ============================================================

def parse_otomoto_fn2(max_price: int, max_mileage: int) -> List[Offer]:
    url = "https://www.otomoto.pl/osobowe/honda/civic/od-2007?search%5Bfilter_enum_generation%5D=gen-viii-type-r-fn2"

    html = fetch_html(url)
    soup = BeautifulSoup(html, "lxml")

    offers = []

    for card in soup.select("article"):
        title_el = card.select_one("h2")
        link_el = card.select_one("a")
        price_el = card.select_one("span.offer-price__number")
        mileage_el = card.select_one("li[data-code='mileage']")
        year_el = card.select_one("li[data-code='year']")

        if not (title_el and link_el and price_el):
            continue

        title = title_el.get_text(strip=True)
        if "Type R" not in title:
            continue

        url_offer = link_el["href"]

        price = int(price_el.get_text(strip=True).split()[0].replace(" ", ""))
        if price > max_price:
            continue

        mileage = 0
        if mileage_el:
            try:
                mileage = int(mileage_el.get_text(strip=True).split()[0].replace(" ", ""))
            except:
                mileage = 0

        if mileage > max_mileage:
            continue

        year = int(year_el.get_text(strip=True).split()[0]) if year_el else 0

        offers.append(
            Offer("otomoto", title, price, mileage, year, url_offer, "Poland", datetime.utcnow())
        )

    return offers


# ============================================================
#  OLX
# ============================================================

def parse_olx_fn2(max_price: int, max_mileage: int) -> List[Offer]:
    url = "https://www.olx.pl/motoryzacja/samochody/q-honda-civic-type-r-fn2/"

    html = fetch_html(url)
    soup = BeautifulSoup(html, "lxml")

    offers = []

    for card in soup.select("div.offer-wrapper"):
        title_el = card.select_one("h3")
        link_el = card.select_one("a")
        price_el = card.select_one(".price strong")

        if not (title_el and link_el and price_el):
            continue

        title = title_el.get_text(strip=True)
        if "Type R" not in title:
            continue

        url_offer = link_el["href"]

        price = int(price_el.get_text(strip=True).split()[0].replace(" ", ""))
        if price > max_price:
            continue

        offers.append(
            Offer("olx", title, price, 0, 0, url_offer, "Poland", datetime.utcnow())
        )

    return offers


# ============================================================
#  ZAPIS CSV / MD
# ============================================================

def save_offers_csv(offers: List[Offer], path: str):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["created_at", "country", "source", "title", "price", "mileage", "year", "url"])
        for o in offers:
            writer.writerow([
                o.created_at.isoformat(),
                o.country,
                o.source,
                o.title,
                o.price,
                o.mileage,
                o.year,
                o.url,
            ])


def save_offers_md(offers: List[Offer], path: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# FN2 oferty ({datetime.utcnow().isoformat()})\n\n")
        for o in offers:
            f.write(f"- **{o.price}** – {o.year} – {o.mileage} km – {o.title} – [{o.url}]({o.url}) ({o.source})\n")


# ============================================================
#  MAIN – ROZDZIELONE PL / SE
# ============================================================

def main():
    max_price_se = 250_000      # SEK
    max_price_pl = 250_000      # PLN
    max_mileage_km = 300_000

    # Szwecja
    offers_se = []
    offers_se.extend(parse_blocket_rss(max_price_se, max_mileage_km))
    offers_se.extend(parse_wayke_fn2(max_price_se, max_mileage_km))

    # Polska
    offers_pl = []
    offers_pl.extend(parse_otomoto_fn2(max_price_pl, max_mileage_km))
    offers_pl.extend(parse_olx_fn2(max_price_pl, max_mileage_km))

    # Zapis
    save_offers_csv(offers_se, "data/fn2_sweden.csv")
    save_offers_csv(offers_pl, "data/fn2_poland.csv")

    save_offers_md(offers_se, "reports/fn2_sweden_latest.md")
    save_offers_md(offers_pl, "reports/fn2_poland_latest.md")

    print(f"Szwecja: {len(offers_se)} ofert")
    print(f"Polska: {len(offers_pl)} ofert")


if __name__ == "__main__":
    main()
