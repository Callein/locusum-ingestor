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
            # 1. Filter out Sponsored
            if "/sponsored/" in link:
                continue
            
            # 2. Check Article Pattern
            if article_pattern.search(link):
                full_url = response.urljoin(link)
                yield scrapy.Request(full_url, callback=self.parse_article)

    def parse_article(self, response):
        item = RawArticleItem()
        item["url"] = response.url
        item["source"] = "Community Impact"
        
        # Default Region
        item["region"] = "Texas"

        # Extract all H1s to determine Title vs Region
        h1s = response.css('h1::text').getall()
        h1s = [h.strip() for h in h1s if h.strip()]
        
        real_title = None

        if h1s:
            first_h1 = h1s[0]
            if "|" in first_h1:
                # e.g. "| Austin" -> Region: Austin
                item["region"] = first_h1.replace("|", "").strip()
                
                # If there's a second h1, that's the title
                if len(h1s) > 1:
                    real_title = h1s[1]
            else:
                # First H1 is likely the title if no pipe
                real_title = first_h1

        # Fallback if H1 logic failed or no H1s
        if not real_title:
             real_title = response.css('h1.entry-title::text').get()
        if not real_title:
             real_title = response.css('h2.entry-title::text').get()

        item["title"] = real_title.strip() if real_title else None

        # Author & Image
        # Author usually in div.byline-wrapper or meta
        item["author"] = response.css('div.byline-wrapper div::text').get()
        if not item["author"]:
             item["author"] = response.css('meta[name="author"]::attr(content)').get()
        
        item["image_url"] = response.css('meta[property="og:image"]::attr(content)').get()

        # Content
        # Observed: div.blog-post contains the main content
        content = response.css('div.blog-post').get() 
        if not content:
            content = response.css('div.impact-article').get()
        if not content:
            content = response.css('div.post-content').get()
        if not content:
            content = response.css('article').get()

        item["html_content"] = content
        yield item
