# spiders/subreddit_post_meta_json.py
import scrapy
from reddit_scraper.items import RedditPostItem
from reddit_scraper.spiders.constants.start_urls import START_URLS
import logging


class SubredditPostMetaJsonSpider(scrapy.Spider):
    """
    A Scrapy spider that scrapes metadata from posts in multiple subreddits using Reddit's JSON endpoints.

    This spider takes a list of subreddit URLs (START_URLS) and scrapes the following
    metadata for each post in the subreddits:
        - title
        - author
        - comment count
        - permalink
        - created timestamp
        - start_url (the subreddit URL)

    Additionally, it logs the exit IP address, user-agent, and proxy information.
    """
    
    name = "subreddit_post_meta_json"
    start_urls = START_URLS

    custom_settings = {
        "ITEM_PIPELINES": {
            "reddit_scraper.pipelines.SubredditPostMetaSpiderPipeline": 1,
        }
    }

    def start_requests(self):
        for url in self.start_urls:
            json_url = f"{url}.json?limit=100"
            yield scrapy.Request(
                url=json_url,
                callback=self.parse,
                headers={'User-Agent': 'YourAppName/Version by YourUsername'},
                meta={"start_url": url, "json_data": None}
            )

    def parse(self, response):
        data = response.json()
        # Store the JSON data in meta to pass to the next request
        meta = response.meta.copy()
        meta["json_data"] = data

        yield scrapy.Request(
            url="https://httpbin.org/ip",
            callback=self.log_exit_ip_and_continue,
            meta=meta,
            dont_filter=True,
            headers={'User-Agent': 'YourAppName/Version by YourUsername'}
        )

    def log_exit_ip_and_continue(self, response):
        """
        Logs the exit IP, user-agent, and proxy (if used), and extracts the metadata
        of posts from the original subreddit JSON response.

        The metadata extracted includes title, author, comment count, permalink,
        and created timestamp for each post.
        """
        actual_exit_ip = response.json().get("origin")
        original_response_data = response.meta.get("json_data")
        start_url = response.meta.get("start_url")
        proxy = response.meta.get("proxy")

        user_agent = response.request.headers.get("User-Agent", b"").decode("utf-8")

        print("\n" + "=" * 100)
        logging.info(f"User-Agent used: {user_agent}")
        logging.info(f"Exit IP (Tor Node): {actual_exit_ip}")
        if proxy:
            logging.info(f"Proxy IP (Docker): {proxy}")

        posts = original_response_data.get("data", {}).get("children", [])

        for post in posts:
            post_data = post["data"]
            item = RedditPostItem()
            item["title"] = post_data.get("title")
            item["author"] = post_data.get("author")
            item["comments"] = post_data.get("num_comments")
            item["permalink"] = post_data.get("permalink")
            item["created_timestamp"] = post_data.get("created_utc")
            item["start_url"] = start_url
            yield item

        logging.info(f"Scraped {len(posts)} posts from subreddit: {start_url}")

        after = original_response_data.get("data", {}).get("after")
        if after:
            next_page = f"{start_url}.json?after={after}&limit=100"
            yield scrapy.Request(
                url=next_page,
                callback=self.parse,
                headers={'User-Agent': 'YourAppName/Version by YourUsername'},
                meta={"start_url": start_url, "proxy": proxy}
            )

        print("=" * 100 + "\n")