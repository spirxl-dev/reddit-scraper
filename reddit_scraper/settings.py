# Scrapy settings for reddit_scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "reddit_scraper"

LOG_LEVEL = "DEBUG"
LOG_FORMAT = "%(levelname)s: %(message)s"

SPIDER_MODULES = ["reddit_scraper.spiders"]
NEWSPIDER_MODULE = "reddit_scraper.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 4
TORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

ITEM_PIPELINES = {
    "reddit_scraper.pipelines.RedditSpiderPipeline": 300,
}

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}

DOWNLOADER_MIDDLEWARES = {
    "reddit_scraper.middlewares.StealthPlaywrightMiddleware": 100,
    "scrapy_user_agents.middlewares.RandomUserAgentMiddleware": 400,
    "rotating_proxies.middlewares.RotatingProxyMiddleware": 610,
    "rotating_proxies.middlewares.BanDetectionMiddleware": 620,
}

ROTATING_PROXY_LIST_PATH = "proxy-list.txt"
ROTATING_PROXY_PAGE_RETRY_TIMES = 5

START_URLS = [
    'https://www.reddit.com/r/Jokes/new/',
    'https://www.reddit.com/r/explainlikeimfive/new/',
    'https://www.reddit.com/r/LifeProTips/new/',
    'https://www.reddit.com/r/TrueOffMyChest/new/',
    'https://www.reddit.com/r/talesfromtechsupport/new/',
    'https://www.reddit.com/r/AskUK/new/',
    'https://www.reddit.com/r/tifu/new/',
    'https://www.reddit.com/r/AmItheAsshole/new/',
    'https://www.reddit.com/r/legaladvice/new/',
    'https://www.reddit.com/r/whowouldwin/new/',
    'https://www.reddit.com/r/AskReddit/new/',
    'https://www.reddit.com/r/HFY/new/',
    'https://www.reddit.com/r/AskHistorians/new/',
    'https://www.reddit.com/r/talesfromretail/new/',
    'https://www.reddit.com/r/wouldyourather/new/',
    'https://www.reddit.com/r/stories/new/',
    'https://www.reddit.com/r/answers/new/',
    'https://www.reddit.com/r/technology/new/',
    'https://www.reddit.com/r/science/new/',
    'https://www.reddit.com/r/worldnews/new/',
    'https://www.reddit.com/r/interestingasfuck/new/',
    'https://www.reddit.com/r/Futurology/new/',
    'https://www.reddit.com/r/nottheonion/new/',
    'https://www.reddit.com/r/mildlyinteresting/new/',
    'https://www.reddit.com/r/todayilearned/new/',
    'https://www.reddit.com/r/space/new/',
    'https://www.reddit.com/r/IAmA/new/',
    'https://www.reddit.com/r/news/new/',
    'https://www.reddit.com/r/personalfinance/new/',
    'https://www.reddit.com/r/investing/new/',
    'https://www.reddit.com/r/DIY/new/',
    'https://www.reddit.com/r/movies/new/',
    'https://www.reddit.com/r/Documentaries/new/',
    'https://www.reddit.com/r/gaming/new/',
    'https://www.reddit.com/r/PCMasterRace/new/',
    'https://www.reddit.com/r/funny/new/',
    'https://www.reddit.com/r/oddlysatisfying/new/',
    'https://www.reddit.com/r/books/new/',
    'https://www.reddit.com/r/food/new/',
    'https://www.reddit.com/r/cars/new/',
    'https://www.reddit.com/r/Fitness/new/',
    'https://www.reddit.com/r/relationship_advice/new/',
    'https://www.reddit.com/r/NoStupidQuestions/new/',
    'https://www.reddit.com/r/wholesomememes/new/',
    'https://www.reddit.com/r/nosleep/new/',
    'https://www.reddit.com/r/MadeMeSmile/new/',
    'https://www.reddit.com/r/AskMen/new/',
    'https://www.reddit.com/r/AskWomen/new/',
    'https://www.reddit.com/r/CasualConversation/new/',
    'https://www.reddit.com/r/Frugal/new/',
    'https://www.reddit.com/r/DecidingToBeBetter/new/',
    'https://www.reddit.com/r/TwoXChromosomes/new/',
    'https://www.reddit.com/r/Music/new/',
    'https://www.reddit.com/r/Art/new/',
    'https://www.reddit.com/r/wholesome/new/',
    'https://www.reddit.com/r/TrueCrime/new/',
    'https://www.reddit.com/r/StarWars/new/',
    'https://www.reddit.com/r/GameofThrones/new/',
    'https://www.reddit.com/r/mildlyinfuriating/new/',
    'https://www.reddit.com/r/pokemon/new/',
    'https://www.reddit.com/r/anime/new/',
    'https://www.reddit.com/r/marvel/new/',
    'https://www.reddit.com/r/comicbooks/new/',
    'https://www.reddit.com/r/coolguides/new/',
    'https://www.reddit.com/r/ArtPorn/new/',
    'https://www.reddit.com/r/aviation/new/',
    'https://www.reddit.com/r/Baking/new/',
    'https://www.reddit.com/r/Boardgames/new/',
    'https://www.reddit.com/r/Conspiracy/new/',
    'https://www.reddit.com/r/Cooking/new/',
    'https://www.reddit.com/r/Cricket/new/',
    'https://www.reddit.com/r/CryptoCurrency/new/',
    'https://www.reddit.com/r/DataScience/new/',
    'https://www.reddit.com/r/Dogs/new/',
    'https://www.reddit.com/r/DungeonsAndDragons/new/',
    'https://www.reddit.com/r/EarthPorn/new/',
    'https://www.reddit.com/r/ElderScrolls/new/',
    'https://www.reddit.com/r/FoodPorn/new/',
    'https://www.reddit.com/r/Frugal/new/',
    'https://www.reddit.com/r/History/new/',
    'https://www.reddit.com/r/Houseplants/new/',
    'https://www.reddit.com/r/InternetIsBeautiful/new/',
    'https://www.reddit.com/r/LEGO/new/',
    'https://www.reddit.com/r/Minecraft/new/',
    'https://www.reddit.com/r/Music/new/',
    'https://www.reddit.com/r/Outdoors/new/',
    'https://www.reddit.com/r/Pareidolia/new/',
    'https://www.reddit.com/r/photography/new/',
    'https://www.reddit.com/r/physics/new/',
    'https://www.reddit.com/r/Programming/new/',
    'https://www.reddit.com/r/RealityTv/new/',
    'https://www.reddit.com/r/Running/new/',
    'https://www.reddit.com/r/Showerthoughts/new/',
    'https://www.reddit.com/r/Sketches/new/',
    'https://www.reddit.com/r/Sneakers/new/',
    'https://www.reddit.com/r/Sports/new/',
    'https://www.reddit.com/r/StarTrek/new/',
    'https://www.reddit.com/r/StrangerThings/new/',
    'https://www.reddit.com/r/Succulents/new/',
    'https://www.reddit.com/r/TechNews/new/',
    'https://www.reddit.com/r/trackandfield/new/',
    'https://www.reddit.com/r/Travel/new/',
    'https://www.reddit.com/r/UrbanPlanning/new/',
    'https://www.reddit.com/r/Vegetarian/new/',
    'https://www.reddit.com/r/Vegan/new/',
    'https://www.reddit.com/r/WatchPeopleDieInside/new/',
    'https://www.reddit.com/r/WebDesign/new/',
    'https://www.reddit.com/r/weightlifting/new/',
    'https://www.reddit.com/r/woodworking/new/',
    'https://www.reddit.com/r/yoga/new/',
    'https://www.reddit.com/r/Zelda/new/',
]


# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "reddit_scraper.middlewares.RedditSpiderSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "reddit_scraper.middlewares.RedditSpiderDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_S
