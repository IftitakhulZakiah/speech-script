# scrapy crawl quotes -o quotes.json
# scrapy crawl quotes

import scrapy
from tutorial.items import PagesItem, LinkItem

def get_urls(filename):
    urls = open(filename).read().splitlines()
    return urls

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    allowed_domains = ['http://www.bnisyariah.co.id/']
    start_urls = get_urls("bni_syariah/bni_urls2")

    # start_urls = ['https://www.bnisyariah.co.id/id-id/']

    def parse(self, response):
        # with open('bni_syariah/bni_urls2', 'a') as f:
        #     f.write("{}\n".format(response.xpath("//*/a/@href").extract()))

        items = PagesItem()
        items['link'] = response.url
        items['title'] = response.xpath("//title/text()").extract()
        items['content'] = response.xpath("//*/p/descendant-or-self::*/text()").extract() 
        yield(items)