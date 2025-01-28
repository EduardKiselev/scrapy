import scrapy


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        hrefs = response.xpath("//article//h3/a/@href").getall()
        for href in hrefs:
            yield scrapy.Request(
                url=response.urljoin(href), callback=self.parse_book)
            
        next_page_href = response.xpath(
            "//ul[@class='pager']/li[@class='next']/a/@href").get()
        yield scrapy.Request(
            url=response.urljoin(next_page_href), callback=self.parse)

    def parse_book(self, response):
        book_title = response.xpath("//h1/text()").get()
        book_description = response.xpath("//article[@class='product_page']/p/text()").get()
        return {"book_title": book_title, "book_descr": book_description}


