from scrapy import Spider, Request
from reddit_scraper.items import RedditPostItem
from reddit_scraper.spiders.constants.start_urls import START_URLS
import logging
import json
from urllib.parse import urljoin, urlparse


class SubredditPostMetaSpider(Spider):
    """
    A Scrapy spider that scrapes metadata from posts in multiple subreddits using Reddit's JSON endpoints.

    Example use from CLI: 
        scrapy crawl subreddit_post_meta -a max_pages=10

    Features:
        - Scrapes up to `max_pages` (default: 1) pages of posts per subreddit.
        - Saves raw JSON responses and extracted post data to separate files.
        - Logs the exit IP address, user-agent, and proxy information.
        - Logs and prints the number of posts scraped per subreddit.
    """

    name = "subreddit_post_meta"
    start_urls = START_URLS

    custom_settings = {
        "ITEM_PIPELINES": {
            "reddit_scraper.pipelines.SubredditPostMetaSpiderPipeline": 1,
        }
    }

    def __init__(self, max_pages=1, *args, **kwargs):
        """
        Initializes the spider with a maximum number of pages to scrape per subreddit.

        Args:
            max_pages (int): The maximum number of pages (batches of 100 posts) to scrape per subreddit.
                             Defaults to 1.
        """
        super(SubredditPostMetaSpider, self).__init__(*args, **kwargs)
        try:
            self.max_pages = int(max_pages)
            if self.max_pages < 1:
                raise ValueError
        except ValueError:
            self.logger.error("Invalid `max_pages` value provided. It should be a positive integer.")
            self.max_pages = 1 

    def start_requests(self):
        """
        Generates the initial requests for each subreddit with the specified limit and initial page.
        """
        for url in self.start_urls:
            json_url = f"{url}.json?limit=100"
            yield Request(
                url=json_url,
                callback=self.parse,
                meta={
                    "start_url": url,
                    "json_data": None,
                    "page": 1,
                    "max_pages": self.max_pages
                }
            )

    def parse(self, response):
        """
        Parses the JSON response, logs exit IP, and handles pagination.

        Args:
            response (scrapy.http.Response): The HTTP response object.
        """
        try:
            data = response.json()
        except json.JSONDecodeError:
            self.logger.error(f"Failed to decode JSON from {response.url}")
            return

        meta = response.meta.copy()
        meta["json_data"] = data

        yield Request(
            url="https://httpbin.org/ip",
            callback=self.log_exit_ip_and_continue,
            meta=meta,
            dont_filter=True,
        )

    def log_exit_ip_and_continue(self, response):
        """
        Logs the exit IP, user-agent, and proxy (if used), extracts post metadata,
        saves raw and processed data, and handles pagination.

        Args:
            response (scrapy.http.Response): The HTTP response object from httpbin.org/ip.
        """
        try:
            actual_exit_ip = response.json().get("origin")
        except json.JSONDecodeError:
            self.logger.error("Failed to decode JSON from httpbin.org/ip")
            actual_exit_ip = "Unknown"

        original_response_data = response.meta.get("json_data")
        start_url = response.meta.get("start_url")
        current_page = response.meta.get("page", 1)
        max_pages = response.meta.get("max_pages", 1)
        proxy = response.meta.get("proxy")

        user_agent = response.request.headers.get("User-Agent", b"").decode("utf-8")

        logging.info(f"User-Agent used: {user_agent}")
        logging.info(f"Exit IP (Tor Node): {actual_exit_ip}")
        if proxy:
            logging.info(f"Proxy IP (Docker): {proxy}")

        posts = original_response_data.get("data", {}).get("children", [])
        num_posts = len(posts)

        extracted_posts = []
        for post in posts:
            post_data = post["data"]
            item = RedditPostItem()
            item["title"] = post_data.get("title")
            item["author"] = post_data.get("author")
            item["comments"] = post_data.get("num_comments")
            item["permalink"] = urljoin("https://www.reddit.com", post_data.get("permalink"))
            item["created_timestamp"] = post_data.get("created_utc")
            item["start_url"] = start_url
            yield item

            extracted_post = {
                "title": item["title"],
                "author": item["author"],
                "comments": item["comments"],
                "permalink": item["permalink"],
                "created_timestamp": item["created_timestamp"],
                "start_url": item["start_url"]
            }
            extracted_posts.append(extracted_post)

        logging.info(f"Scraped {num_posts} posts from subreddit: {start_url} (Page {current_page})")

        subreddit_name = self.get_subreddit_name(start_url)
        posts_filename = f"{subreddit_name}_posts.json"

        try:
            with open(posts_filename, "a", encoding='utf-8') as posts_file:
                for post in extracted_posts:
                    json.dump(post, posts_file)
                    posts_file.write("\n")
            logging.info(f"Appended extracted post data to {posts_filename}")
        except IOError as e:
            self.logger.error(f"Error saving extracted post data to {posts_filename}: {e}")

        after = original_response_data.get("data", {}).get("after")
        if after and current_page < max_pages:
            next_page = current_page + 1
            next_json_url = f"{start_url}.json?after={after}&limit=100"
            yield Request(
                url=next_json_url,
                callback=self.parse,
                meta={
                    "start_url": start_url,
                    "json_data": None,
                    "page": next_page,
                    "max_pages": max_pages,
                    "proxy": proxy
                }
            )
        elif after and current_page >= max_pages:
            logging.info(f"Reached max_pages={max_pages} for subreddit: {start_url}")
        else:
            logging.info(f"No more pages to scrape for subreddit: {start_url}")

    def get_subreddit_name(self, url):
        """
        Extracts the subreddit name from the given URL.

        Args:
            url (str): The subreddit URL.

        Returns:
            str: The subreddit name.
        """
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip("/").split("/")
        if len(path_parts) >= 2 and path_parts[0].lower() == 'r':
            return path_parts[1]
        return "unknown_subreddit"