import scrapy

class RawArticleItem(scrapy.Item):
    url = scrapy.Field()
    source = scrapy.Field()
    title = scrapy.Field()
    html_content = scrapy.Field()
