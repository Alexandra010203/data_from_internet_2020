#Источник https://auto.youla.ru/
#Обойти все марки авто и зайти на странички объявлений
#Собрать след стуркутру и сохранить в БД Монго
#Название объявления
#Список фото объявления (ссылки)
#Список характеристик
#Описание объявления
#ссылка на автора объявления
#дополнительно попробуйте вытащить телефона'

import re
import scrapy
import pymongo
#from ..loaders import AutoYoulaLoader


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    db_type = 'MONGO'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']


    ccs_query = {
        'brands': 'div.ColumnItemList_container__5gTrc div.ColumnItemList_column__5gjdt a.blackLink',
        'pagination': '.Paginator_block__2XAPy a.Paginator_button__u1e7D',
        'ads': 'article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu'



#@@ -14,41 +15,33 @@ class AutoyoulaSpider(scrapy.Spider):
 #       'ads': 'article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu'
 #   }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = pymongo.MongoClient()['parse_gb'][self.name]

    itm_template = {
        'title': '//div[@data-target="advert-title"]/text()',
        'images': '//figure[contains(@class, "PhotoGallery_photo")]//img/@src',
        'description': '//div[contains(@class, "AdvertCard_descriptionInner")]//text()',
        'autor': '//script[contains(text(), "window.transitState =")]/text()',
        'specifications':
            '//div[contains(@class, "AdvertCard_specs")]/div/div[contains(@class, "AdvertSpecs_row")]',
    }

# def __init__(self, *args, **kwargs):
#     super().__init__(*args, **kwargs)

    def parse(self, response):
        for brand in response.css(self.ccs_query['brands']):
            yield response.follow(brand.attrib.get('href'), callback=self.brand_page_parse)

    def brand_page_parse(self, response):
        for pag_page in response.css(self.ccs_query['pagination']):
            yield response.follow(pag_page.attrib.get('href'), callback=self.brand_page_parse)
        # for pag_page in response.css(self.ccs_query['pagination']):
        #     yield response.follow(pag_page.attrib.get('href'), callback=self.brand_page_parse)

        for ads_page in response.css(self.ccs_query['ads']):
            yield response.follow(ads_page.attrib.get('href'), callback=self.ads_parse)

    def ads_parse(self, response):
        data = {
            'title': response.css('.AdvertCard_advertTitle__1S1Ak::text').get(),
            'images': [img.attrib.get('src') for img in response.css('figure.PhotoGallery_photo__36e_r img')],
            'description': response.css('div.AdvertCard_descriptionInner__KnuRi::text').get(),
            'url': response.url,
            'autor': self.js_decoder_autor(response),
            'specification': self.get_specifications(response),
        }
#        loader = AutoYoulaLoader(response=response)
#        loader.add_value('url', response.url)
#        for name, selector in self.itm_template.items():
#            loader.add_xpath(name, selector)

        self.db.insert_one(data)

    def get_specifications(self, response):
        return {itm.css('.AdvertSpecs_label__2JHnS::text').get(): itm.css(
            '.AdvertSpecs_data__xK2Qx::text').get() or itm.css('a::text').get() for itm in
                response.css('.AdvertSpecs_row__ljPcX')}

    def js_decoder_autor(self, response):
        # script = response.xpath('//script[contains(text(), "window.transitState =")]/text()').get()
        script = response.css('script:contains("window.transitState = decodeURIComponent")::text').get()
        re_str = re.compile(r"youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar")
        result = re.findall(re_str, script)
        return f'https://youla.ru/user/{result[0]}' if result else None
        yield loader.load_item()
