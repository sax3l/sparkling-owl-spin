import requests
import gzip
import io
import time
import csv
from bs4 import BeautifulSoup

# Anpassad User-Agent för att likna en vanlig webbläsare
CUSTOM_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) "
        "Gecko/20100101 Firefox/108.0"
    )
}

def fetch_sitemap_content(url):
    """
    Hämtar innehållet från en sitemap-URL.
    Om filen är komprimerad (.gz) packas den upp i minnet.
    Returnerar XML-innehållet som en sträng.
    """
    try:
        response = requests.get(url, headers=CUSTOM_HEADERS, timeout=20, stream=True)
        response.raise_for_status()
    except Exception as e:
        raise Exception(f"Fel vid hämtning av {url}: {e}")
    
    # Om filen är komprimerad (slutar med .gz) packar vi upp den
    if url.endswith('.gz'):
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
                xml_data = f.read().decode('utf-8', errors='replace')
        except Exception as e:
            raise Exception(f"Fel vid uppackning av {url}: {e}")
    else:
        # Vanlig text (XML eller HTML)
        xml_data = response.text

    return xml_data

def parse_sitemap(xml_data):
    """
    Tolkar XML-innehållet och returnerar två listor:
      - sitemap_links: länkar till undersitemaps (i <sitemap><loc>...</loc></sitemap>)
      - url_links: slutliga URL:er (i <url><loc>...</loc></url>)

    OBS! Om Bytbil-sitemapen inte följer standard-XML kan du behöva ändra logiken.
    """
    soup = BeautifulSoup(xml_data, "lxml-xml")
    
    # Leta efter <sitemap><loc>...<loc></sitemap>
    sitemap_links = []
    for sitemap_tag in soup.find_all("sitemap"):
        loc = sitemap_tag.find("loc")
        if loc:
            sitemap_links.append(loc.text.strip())
    
    # Leta efter <url><loc>...<loc></url>
    url_links = []
    for url_tag in soup.find_all("url"):
        loc = url_tag.find("loc")
        if loc:
            url_links.append(loc.text.strip())
    
    return sitemap_links, url_links

def crawl_all_sitemaps(start_sitemaps, delay=1):
    """
    Går igenom alla sitemaps och samlar slutliga URL:er.
    delay anger sekunder mellan anrop (för att undvika att belasta servern för hårt).
    Returnerar en set med unika URL:er.
    """
    visited = set()      # Håller koll på redan besökta sitemap-URL:er
    final_urls = set()   # Samlar slutliga URL:er
    queue = list(start_sitemaps)

    while queue:
        sitemap_url = queue.pop(0)
        if sitemap_url in visited:
            continue
        visited.add(sitemap_url)
        print(f"Bearbetar: {sitemap_url}")
        
        try:
            xml_data = fetch_sitemap_content(sitemap_url)
            new_sitemaps, urls = parse_sitemap(xml_data)
            
            # Lägg till hittade undersitemaps i kön
            for sm in new_sitemaps:
                if sm not in visited:
                    queue.append(sm)
            
            # Lägg till slutliga URL:er
            final_urls.update(urls)
        except Exception as e:
            print(e)
        
        time.sleep(delay)
    
    return final_urls

def save_urls_to_csv(urls, filename="hittade_urler_bytbil.csv"):
    """
    Sparar en uppsättning URL:er i en CSV-fil (en URL per rad).
    """
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        for url in sorted(urls):
            writer.writerow([url])
    print(f"Sparade {len(urls)} URL:er i filen '{filename}'.")

if __name__ == "__main__":
    # Lista över Bytbil-sitemaps
    start_sitemaps = [
        "https://www.bytbil.com/sitemap-bil",
        "https://www.bytbil.com/sitemap-transportbil",
        "https://www.bytbil.com/sitemap-mc",
        "https://www.bytbil.com/sitemap-moped",
        "https://www.bytbil.com/sitemap-atv",
        "https://www.bytbil.com/sitemap-snoskoter",
        "https://www.bytbil.com/sitemap-husbil",
        "https://www.bytbil.com/sitemap-husvagn",
        "https://www.bytbil.com/sitemap-slapvagn",
        "https://www.bytbil.com/sitemap-artiklar"
    ]
    
    print("Startar skrapning av Bytbil-sitemaps...")
    all_urls = crawl_all_sitemaps(start_sitemaps, delay=1)
    print(f"Totalt antal slutliga URL:er hittade: {len(all_urls)}")
    
    # Spara i CSV-fil
    save_urls_to_csv(all_urls, "hittade_urler_bytbil.csv")
