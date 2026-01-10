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


def parse_blocket_fn2(max_price: int, max_mileage: int) -> List[Offer]:
    url = (
        "https://www.blocket.se/annonser/hela_sverige/fordon/bilar?"
        "q=Honda%20Civic%20Type%20R%20FN2"
    )

    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    offers = []

    for card in soup.select("article"):
        title_el = card.select_one("h2")
        link_el = card.select_one("a")
        price_el = card.select_one(".price")
        mileage_el = card.select_one(".mileage")
        year_el = card.select_one(".year")

        if not (title_el and link_el and price_el):
            continue

        title = title_el.get_text(strip=True)
        if "FN2" not in title:
            continue

        url_offer = "https://www.blocket.se" + link_el["href"]

        price_text = price_el.get_text(strip=True).replace(" ", "").replace("kr", "")
        try:
            price = int(price_text)
        except ValueError:
            continue

        if price > max_price:
            continue

        mileage = None
        if mileage_el:
            mileage_text = mileage_el.get_text(strip=True).replace(" ", "").replace("mil", "")
            try:
                mileage = int(mileage_text)
            except ValueError:
                mileage = None

        if mileage is not None and mileage > max_mileage:
            continue

        year = None
        if year_el:
            try:
                year = int(year_el.get_text(strip=True)[:4])
            except ValueError:
                year = None

        offers.append(
            Offer(
                source="blocket",
                title=title,
                price=price,
                mileage=mileage or 0,
                year=year or 0,
                url=url_offer,
                country="Sweden",
                created_at=datetime.utcnow()
            )
        )

    return offers


def get_all_offers(max_price: int, max_mileage: int) -> List[Offer]:
    offers = []
    offers.extend(parse_blocket_fn2(max_price, max_mileage))
    offers_sorted = sorted(offers, key=lambda o: o.price)
    return offers_sorted


def save_offers_csv(offers: List[Offer], path: str):
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
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


def main():
    max_price_sek = 100_000
    max_mileage_km = 150_000

    offers = get_all_offers(max_price_sek, max_mileage_km)

    save_offers_csv(offers, "data/fn2_sweden.csv")
    save_offers_md(offers, "reports/fn2_sweden_latest.md")


if __name__ == "__main__":
    main()
