
import unittest
from scrapy.http import HtmlResponse, Request
from locusum_ingestor.items import RawArticleItem
from locusum_ingestor.spiders.texas_tribune import TexasTribuneSpider
from locusum_ingestor.spiders.dallas_news import DallasNewsSpider
from locusum_ingestor.spiders.community_impact import CommunityImpactSpider
from locusum_ingestor.spiders.houston_chronicle import HoustonChronicleSpider
import asyncio

class TestSpiders(unittest.TestCase):
    
    def test_texas_tribune_parse(self):
        spider = TexasTribuneSpider()
        html = """
        <html>
            <body>
                <h2 class="entry-title"><a href="/2025/12/05/article1/">Article 1</a></h2>
                <h3 ><a href="/2025/12/05/article2/">Article 2</a></h3>
            </body>
        </html>
        """
        response = HtmlResponse(url="https://www.texastribune.org/", body=html, encoding='utf-8')
        results = list(spider.parse(response))
        self.assertEqual(len(results), 2)
        urls = [r.url for r in results]
        self.assertTrue(any("/2025/12/05/article1/" in u for u in urls))
        self.assertTrue(any("/2025/12/05/article2/" in u for u in urls))

    def test_texas_tribune_article(self):
        spider = TexasTribuneSpider()
        html = """
        <html>
            <body>
                <h1 class="entry-title">Test Title</h1>
                <div class="entry-content"><p>Content</p></div>
            </body>
        </html>
        """
        response = HtmlResponse(url="https://www.texastribune.org/article", body=html, encoding='utf-8')
        results = list(spider.parse_article(response))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "Test Title")
        self.assertIn("Content", results[0]['html_content'])

    def test_dallas_news_parse(self):
        spider = DallasNewsSpider()
        html = """
        <html>
            <body>
                <a href="/news/2025/12/05/test-slug/">Valid Article</a>
                <a href="/other/link">Invalid</a>
            </body>
        </html>
        """
        response = HtmlResponse(url="https://www.dallasnews.com/", body=html, encoding='utf-8')
        results = list(spider.parse(response))
        self.assertEqual(len(results), 1)
        self.assertIn("/news/2025/12/05/test-slug/", results[0].url)

    def test_dallas_news_article(self):
        spider = DallasNewsSpider()
        html = """
        <html>
            <body>
                <h1>Dallas Title</h1>
                <div class="article-body"><p>Dallas Content</p></div>
            </body>
        </html>
        """
        response = HtmlResponse(url="https://www.dallasnews.com/article", body=html, encoding='utf-8')
        results = list(spider.parse_article(response))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "Dallas Title")

    def test_community_impact_parse(self):
        spider = CommunityImpactSpider()
        html = """
        <html>
            <body>
                <a href="/metro/city/cat/2025/12/05/slug/">Valid</a>
                <a href="/about-us">Invalid</a>
            </body>
        </html>
        """
        response = HtmlResponse(url="https://communityimpact.com/", body=html, encoding='utf-8')
        results = list(spider.parse(response))
        self.assertEqual(len(results), 1)
        self.assertIn("/2025/12/05/slug/", results[0].url)

    def test_houston_chronicle_parse(self):
        # Houston Chronicle uses async parse but logic is similar if we mock response
        spider = HoustonChronicleSpider()
        
        # Async test helper
        async def run_test():
            html = """
            <html>
                <body>
                    <a href="/news/houston-texas/article/slug-12345.php">Valid</a>
                    <a href="/subscribe">Invalid</a>
                </body>
            </html>
            """
            # We mock the response.meta["playwright_page"] to avoid error in parse
            # But wait, parse calls page.close(). We need to mock that.
            
            class MockPage:
                async def close(self): pass
            
            req = Request(url="https://www.houstonchronicle.com/", meta={"playwright_page": MockPage()})
            response = HtmlResponse(url="https://www.houstonchronicle.com/", body=html, encoding='utf-8', request=req)
            
            # Since parse is async generator
            results = []
            async for res in spider.parse(response):
                results.append(res)
            
            return results

        results = asyncio.run(run_test())
        self.assertEqual(len(results), 1)
        self.assertIn("/news/houston-texas/article/", results[0].url)

