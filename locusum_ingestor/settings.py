# Scrapy settings for locusum_ingestor project

BOT_NAME = "locusum_ingestor"

SPIDER_MODULES = ["locusum_ingestor.spiders"]
NEWSPIDER_MODULE = "locusum_ingestor.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure Item Pipelines
ITEM_PIPELINES = {
   "locusum_ingestor.pipelines.LocusumIngestorPipeline": 300,
}

# Scrapy-Playwright Configuration
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Playwright Settings
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "timeout": 20000,  # 20 seconds
}

# Logging
LOG_LEVEL = "INFO"

# Set settings module
os_env_settings = "settings"
