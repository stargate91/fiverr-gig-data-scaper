# Fiverr Gig Scraper

Simple Python script for scraping data from a Fiverr gig page.

The goal of this project is to practice web scraping with `requests` and
`BeautifulSoup`.

---

## What it does

Given a Fiverr gig URL, the script extracts basic information like:

- categories (breadcrumbs)
- seller level
- rating and number of reviews
- orders in queue
- gig description
- packages (Basic / Standard / Premium)
- FAQ
- snapshot time

The data is returned as a `GigData` dataclass.

---

## Requirements

Python 3.9+

Dependencies:

```
requests
beautifulsoup4
```

Install:

```bash
pip install -r requirements.txt
```

---

## Usage

```python
from scraper import scrape_gig

url = "https://www.fiverr.com/username/gig-name"
data = scrape_gig(url)

print(data)
```

---

## Notes

- Uses HTML scraping (no official Fiverr API)
- Includes a small delay to avoid sending requests too fast
- Selectors may break if Fiverr changes the page layout
