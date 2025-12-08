import scrapy
from locusum_ingestor.items import RawArticleItem
import re

class CommunityImpactSpider(scrapy.Spider):
    name = "community_impact"
    allowed_domains = ["communityimpact.com"]
    start_urls = ["https://communityimpact.com/"]

    def parse(self, response):
        # Pattern: /<metro>/<city>/<category>/YYYY/MM/DD/<slug>/
        # Example: /dallas-fort-worth/mckinney/education/2025/12/05/choose-mckinney-program-drives-enrollment-generates-1m-for-mckinney-isd/
        # Just looking for YYYY/MM/DD is a good safe bet for news articles
        
        article_pattern = re.compile(r'/\d{4}/\d{2}/\d{2}/[\w-]+/?$')

        links = response.css('a::attr(href)').getall()
        for link in links:
            if article_pattern.search(link):
                full_url = response.urljoin(link)
                yield scrapy.Request(full_url, callback=self.parse_article)

    def parse_article(self, response):
        item = RawArticleItem()
        item["url"] = response.url
        item["source"] = "Community Impact"
        
        title = response.css('h1::text').get()
        item["title"] = title.strip() if title else None

        # Content
        # Inspecting structure if possible, but generic fallback is good.
        # Often div.post-content or similar
        content = response.css('div.post-content').get() # Common WordPress-like class
        if not content:
            content = response.css('div.entry-content').get()
        if not content:
            content = response.css('article').get()

        item["html_content"] = content
        yield item
