import os
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from locusum_ingestor.database import create_db_and_tables
from locusum_ingestor.spiders.news_spider import NewsSpider

def main():
    # Set Scrapy settings module
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'locusum_ingestor.settings')

    # 1. Initialize Database
    create_db_and_tables()

    # 2. Get Settings
    settings = get_project_settings()
    
    # 3. Configure Crawler Process
    process = CrawlerProcess(settings)

    # 4. Define arguments (Example)
    # In a real scenario, these might come from CLI args or a config file
    # For demonstration, we use a sample URL if none provided via CLI
    
    start_urls = "https://example.com"
    css_selectors = "title=h1,content=div"

    if len(sys.argv) > 1:
        start_urls = sys.argv[1]
    
    if len(sys.argv) > 2:
        css_selectors = sys.argv[2]

    print(f"Starting crawler for: {start_urls}")
    
    process.crawl(NewsSpider, start_urls=start_urls, css_selectors=css_selectors)
    process.start()

if __name__ == "__main__":
    main()
