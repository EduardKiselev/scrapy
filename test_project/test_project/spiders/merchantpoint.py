import scrapy
from test_project.db_handler import DBHandler


class MerchantpointSpider(scrapy.Spider):
    name = "merchantpoint"
    allowed_domains = ["merchantpoint.ru"]
    start_urls = ["https://merchantpoint.ru/brands/"]

    def __init__(self, *args, **kwargs):
        super(MerchantpointSpider, self).__init__(*args, **kwargs)
        self.db_handler = DBHandler()

    def parse(self, response):
        hrefs = response.xpath("//table[@class='table table-striped']//td/a/@href").getall()
        for href in hrefs:
            print("GO TO ", href)
            yield scrapy.Request(url=response.urljoin(href), callback=self.href_to_point)

        next_page_href = response.xpath("//*[@id='layout-content']//li/a[contains(text(), 'Вперед')]/@href").get()
        if next_page_href:
            yield scrapy.Request(url=response.urljoin(next_page_href), callback=self.parse)

    def href_to_point(self, response):
        data = response.xpath("//div[@id='terminals']//table//tr")
        for row in data:
            mcc = row.xpath(".//td[1]/text()").get()
            name = row.xpath(".//td[2]/a/text()").get()
            address = row.xpath(".//td[3]/text()").get()

            if mcc and name:
                org_description = response.xpath("//*[@id='home']/div/div/div[1]/div/div[2]/div/p[2]/text()").get()
                org_name = response.xpath("//*[@id='layout-content']//h1/text()").get()
                cleaned_data = {
                    'merchant_name': name,
                    'mcc': mcc,
                    'address': address,
                    'org_name': org_name,
                    'org_description': org_description,
                    'source_url': response.url,
                    'geo_coordinates': "нет данных"
                }
   
                status = self.db_handler.save_data(cleaned_data)
                print(status, cleaned_data['merchant_name'])
                self.log(f"{status} record: {cleaned_data['merchant_name']} at {cleaned_data['address']}")
                return cleaned_data
