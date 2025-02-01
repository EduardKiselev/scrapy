from scrapy.spiders import SitemapSpider
import scrapy


class ParsedData(scrapy.Item):
    description = scrapy.Field(default=None)
    publication_year = scrapy.Field()
    publisher = scrapy.Field(default=None)
    isbn = scrapy.Field()
    pages_cnt = scrapy.Field()
    author = scrapy.Field(default=None)
    title = scrapy.Field()
    price_amount = scrapy.Field(default=None)
    price_currency = scrapy.Field(default=None)
    rating_value = scrapy.Field(default=None)
    rating_count = scrapy.Field(default=None)
    source_url = scrapy.Field()
    book_cover = scrapy.Field(default=None)


class ChitaigorodSpider(SitemapSpider):
    name = 'chitaigorod'
    sitemap_urls = [
        'https://www.chitai-gorod.ru/sitemap/products'+str(i)+'.xml' for i in range(35,36)]
    # sitemap_follow = ["/products"]
    sitemap_rules = [("", "parse_products"),]

    custom_settings = {
        "ITEM_PIPELINES": {"test_project.pipelines.MongoPipeline": 100},
        "MONGO_DB": "books",
        "MONGO_USER": "admin12",
        "MONGO_PASSWORD": "adminpass12",
        "MONGO_DB_COLLECTION": "items",
    }

    def parse_products(self, response):
        if response.xpath("//head/meta[@content='book']").get() is None:
            # print("PASS", self.clean_text(response.xpath("//h1 [@itemprop='name']/text()").get()))
            return
        parsed_data = ParsedData()
        data = response
        parsed_data['description'] = data.xpath("//div [@itemprop='description']/article/text()").get()
        parsed_data['publication_year'] = self.clean_text(data.xpath("//span [@itemprop='datePublished']/text()").get())
        parsed_data['publisher'] = self.clean_text(data.xpath("//a [@itemprop='publisher']/text()").get())
        isbn = self.clean_text(data.xpath("//span [@itemprop='isbn']/text()").get())
        if isbn:
            parsed_data['isbn'] = isbn.split(',')[0]
        else:
            parsed_data['isbn'] = "отсутствует"
        parsed_data['book_cover'] = data.xpath(
            "//img [@class='product-info-gallery__poster']/@src").get()
        parsed_data['pages_cnt'] = self.clean_text(data.xpath(
            "//span [@itemprop='numberOfPages']/text()").get())
        parsed_data['author'] = self.clean_text(data.xpath(
            "//span [@itemprop='author']/a/meta/@content").get())
        parsed_data['title'] = self.clean_text(data.xpath(
            "//h1 [@itemprop='name']/text()").get())
        parsed_data['price_amount'] = data.xpath(
            "//span [@itemprop='price']/@content").get()
        parsed_data['rating_value'] = data.xpath(
            "//span [@class='product-review-range__count']/text()").get()
        rating_count = self.clean_text(data.xpath(
            "//div [@itemprop='aggregateRating']/span/text()").get())
        parsed_data['source_url'] = response.url

        if rating_count:
            parsed_data['rating_count'] = rating_count.split()[0]
        price = data.xpath("//span [@itemprop='price']/text()").get()
        if price:
            parsed_data['price_currency'] = data.xpath(
                "//span [@itemprop='price']/text()").get().split()[-1]

        if parsed_data.get('title') and \
            parsed_data.get('publication_year') and\
                parsed_data.get('isbn') and\
                    parsed_data.get('pages_cnt'):
            # if parsed_data.get('rating_value'):
            #     print('YIELD THIS BOOK', parsed_data)
            yield parsed_data
        return
        
    def clean_text(self, text):
        if text:
            return text.replace('\n', '').strip()
        return text
