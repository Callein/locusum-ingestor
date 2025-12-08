import scrapy
from locusum_ingestor.items import RawArticleItem
import re

class DallasNewsSpider(scrapy.Spider):
    name = "dallas_news"
    allowed_domains = ["dallasnews.com"]
    start_urls = ["https://www.dallasnews.com/"]

    def parse(self, response):
        # Extract article links matching pattern /.../YYYY/MM/DD/...
        # Also, restrict to main content areas to avoid footer links if possible, but global is fine for now
        
        # Regex for article URL: /<category>/.../YYYY/MM/DD/<slug>/
        article_pattern = re.compile(r'/\w+(?:/[\w-]+)*/\d{4}/\d{2}/\d{2}/[\w-]+/?$')

        links = response.css('a::attr(href)').getall()
        for link in links:
            if article_pattern.search(link):
                full_url = response.urljoin(link)
                yield scrapy.Request(full_url, callback=self.parse_article)

    def parse_article(self, response):
        item = RawArticleItem()
        item["url"] = response.url
        item["source"] = "Dallas News"
        
        title = response.css('h1::text').get()
        item["title"] = title.strip() if title else None

        # Content extraction - attempting to target the main article body
        # Common classes: .article-body, .article-content, or generic paragraphs
        content = response.css('div.article-body').get()
        if not content:
            # Fallback
            content = response.css('article').get()
        
        if not content:
             content = response.css('body').get()

        item["html_content"] = content
        yield item
