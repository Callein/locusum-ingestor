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
        item["region"] = "Dallas"
        
        # Title
        # User reported null title. H1 might have nested spans. 
        # Using xpath string() to get all text inside H1.
        title = response.xpath('string(//h1)').get()
        item["title"] = title.strip() if title else None

        # Author & Image
        # Author & Image
        # 1. Try JSON-LD (Most Reliable)
        import json
        ld_json_scripts = response.css('script[type="application/ld+json"]::text').getall()
        for script in ld_json_scripts:
            try:
                data = json.loads(script)
                if isinstance(data, dict):
                     # Type often "NewsArticle" or "ReportageNewsArticle"
                     if "author" in data:
                         authors = data["author"]
                         if isinstance(authors, list) and len(authors) > 0:
                             item["author"] = authors[0].get("name")
                             break
                         elif isinstance(authors, dict):
                             item["author"] = authors.get("name")
                             break
            except:
                continue

        # 2. Fallback to CSS selectors if JSON-LD author missing
        if not item["author"]:
            # Author: a tag with cmp-ltrk="Article - Byline" or inside byline-module
            item["author"] = response.css('a[cmp-ltrk="Article - Byline"]::text').get()
        if not item["author"]:
            item["author"] = response.css('div[class*="byline-module"]::text').get()
        if not item["author"]:
             item["author"] = response.css('meta[name="author"]::attr(content)').get()
        
        item["image_url"] = response.css('meta[property="og:image"]::attr(content)').get()

        # Content extraction
        # Browser inspection showed content is in 'p.body-text-paragraph' elements.
        # We can join them or find their container.
        # Let's try to get the container first, often a section.
        content_lines = response.css('p.body-text-paragraph').getall()
        if content_lines:
             # If we found paragraphs, join them or wrap in a div
             content = "<div>" + "".join(content_lines) + "</div>"
        else:
            # Fallback
            content = response.css('div.article-body').get()
            if not content:
                content = response.css('article').get()
            if not content:
                 content = response.css('section').get()

        item["html_content"] = content
        yield item
