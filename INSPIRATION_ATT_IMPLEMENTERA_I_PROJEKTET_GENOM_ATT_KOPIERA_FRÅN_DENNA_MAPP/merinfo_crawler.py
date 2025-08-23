#!/usr/bin/env python3
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor

class MerinfoSpider(scrapy.Spider):
    name = "merinfo"
    allowed_domains = ["merinfo.se"]
    # Starta gärna från startsidan eller direkt från '/foretag/' beroende på behov:
    start_urls = ["https://www.merinfo.se/"]

    # Anpassade inställningar för spidern
    custom_settings = {
        # Spara extraherade URL:er i en JSON-fil med snygg indentering
        "FEEDS": {"urls.json": {"format": "json", "encoding": "utf8", "indent": 4}},
        "DOWNLOAD_DELAY": 1,          # Fördröjning mellan förfrågningar för att undvika överbelastning
        "ROBOTSTXT_OBEY": True,       # Respektera webbplatsens robots.txt
        "LOG_LEVEL": "INFO",
        "DEPTH_LIMIT": 5,             # Begränsa hur djupt crawlingen går, justera vid behov
    }

    def parse(self, response):
        # Använd en LinkExtractor för att hämta alla länkar från sidan
        link_extractor = LinkExtractor(allow_domains=self.allowed_domains)
        links = link_extractor.extract_links(response)

        for link in links:
            full_url = link.url
            # Om URL:en innehåller "/foretag/" – spara den
            if "/foretag/" in full_url:
                yield {"url": full_url}
            # Följ länken för att fortsätta crawlingen
            yield scrapy.Request(full_url, callback=self.parse)

if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(MerinfoSpider)
    process.start()
