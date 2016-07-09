import os

import scrapy


class NepalipatraSpider(scrapy.Spider):
    name = "nepalipatra"

    base_path = "nepalipatra"

    item_selector = "#mp-pusher > section > div > div > div.col-md-9 > div > div.row > div.col-md-8 > div > div > h2 > a::attr('href')"
    content_selector = "#mp-pusher > section > div > div > div.col-md-9 > div > p::text"
    next_page_selector = "#mp-pusher > section > div > div > div.col-md-9 > div > div.row > div.col-md-8 > div > ul > ul > li:last-child > a::attr('href')"

    def __init__(self, category, *args, **kwargs):
        super(NepalipatraSpider, self).__init__(*args, **kwargs)
        base_url = "http://www.nepalipatra.com/category/news/{}"

        if category == "society":
            self.start_urls = [base_url.format("trend/society")]

        self.category_path = os.path.join(NepalipatraSpider.base_path, category)

        if not os.path.exists(self.category_path):
            os.makedirs(self.category_path)

    def parse(self, response):
        self.logger.info("Current URL: {}".format(response.url))

        for href in response.css(NepalipatraSpider.item_selector):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_item)

        # Link for next page
        next_page = response.css(NepalipatraSpider.next_page_selector)

        if(next_page):
            url = next_page[0].extract()

            yield scrapy.Request(url, self.parse)

    def parse_item(self, response):
        self.logger.debug("Parsing content at: {}".format(response.url))

        content = ''.join([p.extract() for p in response.css(NepalipatraSpider.content_selector)])

        file_name = "{}.txt".format(response.url.split("/")[-2])
        file_path = os.path.join(self.category_path, file_name)

        with open(file_path, "w") as file:
            file.write(content.encode("utf8"))
