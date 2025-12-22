# Scrapy settings for locusum_ingestor project

BOT_NAME = "locusum_ingestor"

SPIDER_MODULES = ["locusum_ingestor.spiders"]
NEWSPIDER_MODULE = "locusum_ingestor.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False # Typically needs to be disabled alongside User-Agent rotation if site is strict, but let's just stick to User-Agent first as requested. Or user only asked for UA.
# Actually user said "Update settings.py ... to use a modern, realistic User-Agent".
# And "Ensure Scrapy-Playwright headers are correctly mimicking a real browser".
# Let's keep ROBOTSTXT_OBEY as is unless user asked, but 403 often implies robots issue too. I'll stick to UA first.

ROBOTSTXT_OBEY = True

# User-Agent to avoid 403
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Configure Item Pipelines
ITEM_PIPELINES = {
   "locusum_ingestor.pipelines.LocusumIngestorPipeline": 300,
}

# Downloader Middlewares
DOWNLOADER_MIDDLEWARES = {
   'locusum_ingestor.middlewares.DuplicateCheckMiddleware': 543,
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
