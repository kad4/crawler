import os

import scrapy
from bs4 import BeautifulSoup


class OnlinekhabarSpider(scrapy.Spider):
    name = "onlinekhabar"

    base_path = "onlinekhabar"

    item_selector = "#archlist > div > h2 > a::attr('href')"
    content_selector = "#sing_cont p::text"
    next_page_selector = "#sing_left > div.pg > a.next.page-numbers::attr('href')"

    def __init__(self, category, *args, **kwargs):
        super(OnlinekhabarSpider, self).__init__(*args, **kwargs)
        self.start_urls = ["http://www.onlinekhabar.com/content/{}/".format(category)]
        self.category = category

        self.category_path = os.path.join(OnlinekhabarSpider.base_path, category)

        if not os.path.exists(self.category_path):
            os.makedirs(self.category_path)

    def parse(self, response):
        self.logger.info("Current URL: {}".format(response.url))

        for href in response.css(OnlinekhabarSpider.item_selector):
            url = href.extract()
            yield scrapy.Request(url, callback=self.parse_item)

        # Link for next page
        next_page = response.css(OnlinekhabarSpider.next_page_selector)

        if(next_page):
            url = next_page[0].extract()
            yield scrapy.Request(url, self.parse)

    def parse_item(self, response):
        self.logger.debug("Parsing content at: {}".format(response.url))

        text = response.body

        # Parse content using BeautifulSoup
        soup = BeautifulSoup(text, "lxml")
        soup = soup.find(id="sing_cont")

        # Remove comments
        soup.find(id="comments").decompose()

        content = ''.join([p.get_text() for p in soup.find_all("p")])

        file_name = "{}.txt".format(response.url.split("/")[-2])
        file_path = os.path.join(self.category_path, file_name)

        with open(file_path, "w") as file:
            file.write(content.encode("utf8"))
