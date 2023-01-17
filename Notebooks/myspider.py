from fake_useragent import UserAgent
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
# from scrapy.utils.python import global_object_name

import scrapy
# from scrapy.linkextractors import LinkExtractor
# import sys
# sys.path.append('path/to/module')
# import path

API_KEY = '378d2b00-d774-4869-bf97-325ac3d1de22'

def get_scrapeops_url(url):
    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url

class MySpider(scrapy.Spider):
    name = "lebanon_akhbar"
    start_urls = ["https://www.al-akhbar.com/Editions"]
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
        'path.to.RotateUserAgentMiddleware': 400,
        'path.to.RotateIPMiddleware': 543,
        'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
        'path.to.RotateUserAgentMiddleware': 400,
        'scrapy.downloadermiddleware.retry.RetryMiddleware': None,
        'path.to.RotateIPMiddleware': 543,
        'FEED_URI': 'output.csv',
        'FEED_FORMAT': 'csv',
        }
    }

    # rules = (
    #     Rule(LinkExtractor(restrict_css="container > l-content row archive-issues > l-main columns col-md-12 > editions-page section > archive-days-wrap"), follow=True),
    #     Rule(LinkExtractor(restrict_css=".product_pod > h3 > a"), callback="parse_book")
    # )

    def parse(self, response):

        selector = scrapy.Selector(response)
        links = selector.css('.class day').xpath('@href').extract()
        print(links)
        for link in links:

            next_page_url = selector.css('a.next-page').xpath('@href').extract_first()

            if next_page_url:
                yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse)

class Items(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()


class RotateUserAgentMiddleware(UserAgentMiddleware):

    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        ua = UserAgent()
        request.headers.setdefault('User-Agent', ua.random)

class RotateIPMiddleware(RetryMiddleware):

    def __init__(self, ip=''):
        self.ip = ip

    def process_request(self, request, spider):
        request.meta["proxy"] = "http://" + self.ip
