# -*- coding: utf-8 -*-
import os

import scrapy


class RatopatiSpider(scrapy.Spider):
    name = "ratopati"

    base_path = "ratopati"

    item_selector = "ul.newsList > li > a.title::attr('href')"
    content_selector = "body > div.container > div > div.col-lg-9.col-md-9.col-sm-8.col-xs-12 > div.innerDet > p::text"
    next_page_selector = "ul.pagination > div > a.nextpostslink::attr('href')"

    def __init__(self, category, *args, **kwargs):
        super(RatopatiSpider, self).__init__(*args, **kwargs)
        base_url = "http://www.ratopati.com/{}/"

        if category == "literature":
            self.start_urls = [base_url.format("साहित्य")]
        elif category == "health":
            self.start_urls = [base_url.format("स्वास्थ्य-शैली")]

        self.category_path = os.path.join(RatopatiSpider.base_path, category)

        if not os.path.exists(self.category_path):
            os.makedirs(self.category_path)

    def parse(self, response):
        self.logger.info("Current URL: {}".format(response.url))

        for href in response.css(RatopatiSpider.item_selector):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_item)

        # Link for next page
        next_page = response.css(RatopatiSpider.next_page_selector)

        if(next_page):
            url = next_page[0].extract()

            yield scrapy.Request(url, self.parse)

    def parse_item(self, response):
        self.logger.debug("Parsing content at: {}".format(response.url))

        content = ''.join([p.extract() for p in response.css(RatopatiSpider.content_selector)])

        file_name = "{}.txt".format(response.url.split("/")[-2])
        file_path = os.path.join(self.category_path, file_name)

        with open(file_path, "w") as file:
            file.write(content.encode("utf8"))
