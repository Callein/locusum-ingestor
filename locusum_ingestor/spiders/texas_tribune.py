import scrapy
from locusum_ingestor.items import RawArticleItem

class TexasTribuneSpider(scrapy.Spider):
    name = "texas_tribune"
    allowed_domains = ["texastribune.org"]
    start_urls = ["https://www.texastribune.org/"]

    def parse(self, response):
        # Extract article links from homepage
        # Targeting h2.entry-title a or similar common patterns on their homepage
        links_h2 = response.css('h2.entry-title a::attr(href)').getall()
        # Also check for other common patterns
        links_h3 = response.css('h3 a::attr(href)').getall()
        
        article_links = list(set(links_h2 + links_h3))

        for link in article_links:
            if link:
                full_url = response.urljoin(link)
                yield scrapy.Request(full_url, callback=self.parse_article)

    def parse_article(self, response):
        item = RawArticleItem()
        item["url"] = response.url
        item["source"] = "Texas Tribune"
        item["region"] = "Texas"
        
        # Title
        title = response.css('h1.entry-title::text').get()
        if not title:
            title = response.css('h1::text').get()
        item["title"] = title.strip() if title else None

        # Author
        author = response.css('meta[name="author"]::attr(content)').get()
        if not author:
            author = response.css('p.byline a::text').get()
        item["author"] = author

        # Image
        image = response.css('meta[property="og:image"]::attr(content)').get()
        item["image_url"] = image

        # HTML Content
        # We prefer the republish content if available as it's cleaner
        # It's inside a textarea and html escaped
        republish_content_escaped = response.css('textarea#republication-tracker-tool-shareable-content::text').get()
        
        if republish_content_escaped:
            import html
            item["html_content"] = html.unescape(republish_content_escaped)
        else:
            # Fallback to entry-content
            item["html_content"] = response.css('div.entry-content').get()

        if item["html_content"]:
            yield item
        else:
            self.logger.warning(f"Skipping non-article page: {response.url}")
