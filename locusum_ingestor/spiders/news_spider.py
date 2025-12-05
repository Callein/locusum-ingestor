import scrapy
from locusum_ingestor.items import RawArticleItem
from scrapy_playwright.page import PageMethod

class NewsSpider(scrapy.Spider):
    name = "news_spider"

    def __init__(self, start_urls=None, css_selectors=None, *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        
        if start_urls:
            if isinstance(start_urls, str):
                self.start_urls = start_urls.split(",")
            else:
                self.start_urls = start_urls
        else:
            self.start_urls = []
            
        # css_selectors expected format: "title=h1.title,content=div.article-body"
        self.selectors = {}
        if css_selectors:
            if isinstance(css_selectors, dict):
                self.selectors = css_selectors
            elif isinstance(css_selectors, str):
                for part in css_selectors.split(","):
                    if "=" in part:
                        key, val = part.split("=", 1)
                        self.selectors[key.strip()] = val.strip()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True, 
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "networkidle")
                    ],
                },
                callback=self.parse
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        
        # Extract title
        title_selector = self.selectors.get("title", "title")
        title = response.css(title_selector + "::text").get()
        if not title:
            title = response.css("title::text").get()

        # Extract content (raw HTML of the body or specific selector)
        # If content selector is provided, use it, otherwise use body
        content_selector = self.selectors.get("content", "body")
        html_content = response.css(content_selector).get()
        
        if not html_content:
            html_content = response.text

        await page.close()

        item = RawArticleItem()
        item["url"] = response.url
        item["source"] = self.name # Or extract domain
        item["title"] = title.strip() if title else None
        item["html_content"] = html_content
        
        yield item
