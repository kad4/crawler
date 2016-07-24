import os

import scrapy


class UjyaaloonlineSpider(scrapy.Spider):
    name = "ujyaaloonline"

    base_path = "ujyaaloonline"

    item_selector = "#texts_aboutus > ul.news_list_full > li > a:nth-child(1)::attr('href')"
    content_selector = "#texts_aboutus > div > div.detailbox > p::text"
    next_page_selector = "#texts_aboutus > ul.pagination > li:nth-last-child(2) > a::attr('href')"

    def __init__(self, category, *args, **kwargs):
        super(UjyaaloonlineSpider, self).__init__(*args, **kwargs)
        base_url = "http://ujyaaloonline.com/news/category/{}"

        if category == "kala":
            self.start_urls = [base_url.format("29/sahitya-kala/")]

        self.category_path = os.path.join(UjyaaloonlineSpider.base_path, category)

        if not os.path.exists(self.category_path):
            os.makedirs(self.category_path)

    def parse(self, response):
        self.logger.info("Current URL: {}".format(response.url))

        for href in response.css(UjyaaloonlineSpider.item_selector):
            url = href.extract()
            yield scrapy.Request(url, callback=self.parse_item)

        # Link for next page
        next_page = response.css(UjyaaloonlineSpider.next_page_selector)

        if(next_page):
            url = next_page[0].extract()

            yield scrapy.Request(url, self.parse)

    def parse_item(self, response):
        self.logger.debug("Parsing content at: {}".format(response.url))

        content = ''.join([p.extract() for p in response.css(UjyaaloonlineSpider.content_selector)])

        file_name = "{}.txt".format(response.url.split("/")[-2])
        file_path = os.path.join(self.category_path, file_name)

        with open(file_path, "w") as file:
            file.write(content.encode("utf8"))
