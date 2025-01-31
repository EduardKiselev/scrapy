import scrapy
import time
import pprint
from scrapy.spiders import SitemapSpider


class ChitaigorodSpider(SitemapSpider):
    name = 'chitaigorod'
    sitemap_urls = ['https://www.chitai-gorod.ru/sitemap/products'+str(i)+'.xml' for i in range(4,5)]
    sitemap_follow = ["/products"]
    #sitemap_urls = ['https://www.chitai-gorod.ru/sitemap/products15.xml']
    sitemap_rules = [("", "parse_products"),]

    custom_settings = {
        "ITEM_PIPELINES": {"test_project.pipelines.CleanData":100,
                           "test_project.pipelines.MongoPipeline": 100},
        "MONGO_DB" :"books",
        "MONGO_USER" :"admin12",
        "MONGO_PASSWORD":"adminpass12",
        "MONGO_DB_COLLECTION": "items",
    }
    
    # Обрабатываем каждую страницу, найденную в отфильтрованных sitemap
    def parse_products(self, response):
        if response.xpath("//head/meta[@content='book']").get() is None:
            print("==============")
            print("НЕТО")
            print(self.clean_text(response.xpath("//h1 [@itemprop='name']/text()").get()))
            print("==============")
            return
        # print("WE IN",response.url)
        parsed_data = {}
        data = response
        # data = response.xpath("//section[@class='detail-product__description-wrapper']")
        # for elem in data:
        parsed_data['description'] = data.xpath("//div [@itemprop='description']/article/text()").get()
        parsed_data['pub_date'] = self.clean_text(data.xpath("//span [@itemprop='datePublished']/text()").get())
        parsed_data['publisher'] = self.clean_text(data.xpath("//a [@itemprop='publisher']/text()").get())
        parsed_data['ISBN'] = self.clean_text(data.xpath("//span [@itemprop='isbn']/text()").get())
        parsed_data['book_cover'] = data.xpath("//img [@class='product-info-gallery__poster']/@src").get()
        parsed_data['number_of_pages'] = self.clean_text(data.xpath("//span [@itemprop='numberOfPages']/text()").get())
        parsed_data['author'] = self.clean_text(data.xpath("//span [@itemprop='author']/a/meta/@content").get())
        parsed_data['title'] = self.clean_text(data.xpath("//h1 [@itemprop='name']/text()").get())
        parsed_data['source_url'] = response.url
        parsed_data['price_amount'] = data.xpath("//span [@itemprop='price']/@content").get()
        parsed_data['rating_value'] = data.xpath("//span [@class='product-review-range__count']").get()
        parsed_data['rating_count'] = self.clean_text(data.xpath("//div [@itemprop='aggregateRating']/text()").get())
        price = data.xpath("//span [@itemprop='price']/@text").get()
        if price:
            parsed_data['price_currency'] = data.xpath("//span [@itemprop='price']/text()").get().split()[-1]
        print('========================')
        if parsed_data['author']:
            print(parsed_data['title'])
            print(parsed_data['author'])
            print(parsed_data['source_url'])
        print('========================')
        yield parsed_data
        

    def clean_text(self, text):
        if text:
            return text.replace('\n', '').strip()
        return text


# title Название книги Да ++++++
# author Автор Нет ++++++
# description Описание Нет +++++
# price_amount Цена Нет +++++
# price_currency Валюта Нет +++++
# rating_value Средняя цена Нет +++++
# rating_count Количество оценок Нет
# publication_year Год публикации Да ++++++
# isbn ISBN Да   ++++++++
# pages_cnt Количество страниц Да +++++++
# publisher Издательство Нет  ++++++++
# book_cover Обложка книги (ссылка на картинку)Нет +++++
# source_url Ссылка на источник данных Да  +++++