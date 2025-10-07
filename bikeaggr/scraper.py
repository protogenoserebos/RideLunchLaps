import requests
from bs4 import BeautifulSoup

URL = "https://www.pinkbike.com/buysell/list/?category=102"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def scrape_listings(url):
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")

    listings = []
    for row in soup.select("div.bsitem"):  # each listing block
        title = row.select_one("a").get_text(strip=True)
        link = "https://www.pinkbike.com" + row.select_one("a")["href"]
        price = row.select_one("div.bsitem-price").get_text(strip=True)
        location = row.select_one("div.bsitem-location").get_text(strip=True)

        listings.append({
            "title": title,
            "price": price,
            "location": location,
            "url": link
        })
    return listings

data = scrape_listings(URL)
for d in data[:5]:
    print(d)