import scrapy

class RawArticleItem(scrapy.Item):
    url = scrapy.Field()
    source = scrapy.Field()
    region = scrapy.Field()
    author = scrapy.Field()
    image_url = scrapy.Field()
    title = scrapy.Field()
    html_content = scrapy.Field()
