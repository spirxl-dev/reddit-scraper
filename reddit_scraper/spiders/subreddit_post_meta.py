from scrapy import Spider, Request
from reddit_scraper.items import RedditPostItem
from reddit_scraper.settings import START_URLS
from scrapy_playwright.page import PageMethod
import logging


class RedditSubredditMetaSpider(Spider):
    """
    A Scrapy spider that scrapes metadata from posts in multiple subreddits.

    This spider takes a list of subreddit URLs (START_URLS) and scrapes the following
    metadata for each post in the subreddits:
        - title
        - author
        - comment count
        - permalink
        - created timestamp
        - start_url (the subreddit URL)

    The gathered metadata can be used for further processing or detailed scraping.
    """
    name = "subreddit_post_meta"
    start_urls = START_URLS

    def start_requests(self):
        """
        Sends requests for each subreddit URL from the `start_urls` list using Playwright.
        """
        for url in self.start_urls:
            yield Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod(
                            "evaluate", "window.scrollBy(0, window.innerHeight * 60);"
                        ),
                        PageMethod("wait_for_load_state", "networkidle"),
                        PageMethod(
                            "add_init_script",
                            """
                            Object.defineProperty(navigator, 'webdriver', {
                              get: () => undefined
                            });
                        """,
                        ),
                    ],
                    "start_url": url,
                },
            )

    async def parse(self, response):
        """
        Makes an additional request to check the exit node IP address and then
        continues to process the subreddit posts metadata from the original response.
        """
        yield Request(
            url="https://httpbin.org/ip",
            callback=self.log_exit_ip_and_continue,
            meta={"original_response": response},
            dont_filter=True,
        )

    def log_exit_ip_and_continue(self, response):
        """
        Logs the exit IP, user-agent, and proxy (if used), and extracts the metadata 
        of posts from the original subreddit response.

        The metadata extracted includes title, author, comment count, permalink, 
        and created timestamp for each post.
        """
        actual_exit_ip = response.json().get("origin")
        original_response = response.meta["original_response"]
        start_url = original_response.meta["start_url"]
        proxy = original_response.meta.get("proxy")

        user_agent = original_response.request.headers.get("User-Agent", b"").decode(
            "utf-8"
        )

        print("\n" + "=" * 138)
        logging.info(f"User-Agent used: {user_agent}")
        logging.info(f"Exit IP (Tor Node): {actual_exit_ip}")
        if proxy:
            logging.info(f"Proxy IP (Docker): {proxy}")
        posts = original_response.css("shreddit-post")

        for post in posts:
            postItem = RedditPostItem()
            postItem["title"] = post.attrib.get("post-title")
            postItem["author"] = post.attrib.get("author")
            postItem["comments"] = post.attrib.get("comment-count")
            postItem["permalink"] = post.attrib.get("permalink")
            postItem["created_timestamp"] = post.attrib.get("created-timestamp")
            postItem["start_url"] = start_url
            yield postItem

        logging.info(f"Scraped all posts from subreddit: {start_url}")
        print("=" * 138 + "\n")