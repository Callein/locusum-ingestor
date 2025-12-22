import scrapy
from locusum_ingestor.items import RawArticleItem
from scrapy_playwright.page import PageMethod

class HoustonChronicleSpider(scrapy.Spider):
    name = "houston_chronicle"
    allowed_domains = ["houstonchronicle.com"]
    start_urls = ["https://www.houstonchronicle.com/"]
    
    custom_settings = {
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": True,
            "timeout": 30000,
        },
        "DOWNLOAD_DELAY": 2,
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "domcontentloaded"),
                        # Attempt to wait for some content
                        # PageMethod("wait_for_selector", "a[href*='/article/']", timeout=5000), 
                    ],
                },
                callback=self.parse
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        
        # Look for article links. 
        # Common pattern: /news/.../article/... or /local/.../article/...
        # or just anything containing /article/
        
        links = response.css('a::attr(href)').getall()
        for link in links:
            if "/article/" in link or ("/news/" in link and link.count("/") > 4):
                 full_url = response.urljoin(link)
                 if "houstonchronicle.com" in full_url:
                     yield scrapy.Request(
                         full_url,
                         meta={
                             "playwright": True,
                             "playwright_include_page": True,
                         },
                         callback=self.parse_article
                     )
        
        await page.close()

    async def parse_article(self, response):
        page = response.meta["playwright_page"]
        
        item = RawArticleItem()
        item["url"] = response.url
        item["source"] = "Houston Chronicle"
        item["region"] = "Houston"
        
        title = response.css('h1::text').get()
        item["title"] = title.strip() if title else None
        
        # Author & Image
        item["author"] = response.css('meta[name="author"]::attr(content)').get() or response.css('.author-name::text').get()
        item["image_url"] = response.css('meta[property="og:image"]::attr(content)').get()

        # Content
        # Hearst sites often use .article-body or section.body
        content = response.css('section.body').get()
        if not content:
            content = response.css('div.article-body').get()
        if not content:
            content = response.css('article').get()

        item["html_content"] = content
        
        await page.close()
        yield item
