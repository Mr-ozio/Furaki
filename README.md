# FN2 Finder

Automatyczny system do monitorowania ofert sprzedaży **Honda Civic Type R FN2** w Polsce i Szwecji.

## 🔧 Co robi ten projekt?

- Przeszukuje codziennie 5 portali ogłoszeniowych:
  - Blocket.se
  - Bytbil.com
  - Wayke.se
  - Otomoto.pl
  - OLX.pl
- Filtruje oferty według:
  - rocznika (2007–2010)
  - koloru (czerwony)
  - ceny (do 100 000 SEK)
  - przebiegu (do 150 000 km)
- Zapisuje wyniki do:
  - `data/fn2_sweden.csv`
  - `data/fn2_poland.csv`
  - `reports/fn2_sweden_latest.md`
  - `reports/fn2_poland_latest.md`
- Analizuje trendy cenowe FN2 w Polsce i Szwecji
- Automatycznie commituje wyniki do repozytorium

## 🚀 Jak to działa?

System uruchamiany jest codziennie przez GitHub Actions (`.github/workflows/fn2_finder.yml`).

Główne skrypty:

- `src/fn2_scraper.py` – zbiera i filtruje oferty
- `src/fn2_trend.py` – analizuje trendy cenowe

## 📦 Wymagane biblioteki

Zdefiniowane w `requirements.txt`:
