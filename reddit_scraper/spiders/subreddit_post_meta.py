import logging
import sqlite3
from json import JSONDecodeError
from urllib.parse import urljoin

from scrapy import Spider, Request
from scrapy.exceptions import CloseSpider
from scrapy.utils.project import get_project_settings
from reddit_scraper.items import RedditPostItem


class SubredditPostMetaSpider(Spider):
    """
    A Scrapy spider that scrapes metadata from posts in multiple subreddits using Reddit's JSON endpoints.

    Example use from CLI:
        scrapy crawl subreddit_post_meta -a max_pages=10
    """

    name = "subreddit_post_meta"

    custom_settings = {
        "ITEM_PIPELINES": {
            "reddit_scraper.pipelines.SubredditPostMetaPipeline": 1,
        }
    }

    def __init__(self, max_pages=1, *args, **kwargs):
        """
        Initialises the spider with a maximum number of pages to scrape per subreddit.

        Args:
            max_pages (int): The maximum number of pages (each page is a batch of approx 100 posts) to scrape per subreddit.
                             Defaults to 1 page.
        """
        super(SubredditPostMetaSpider, self).__init__(*args, **kwargs)

        self.max_pages = int(max_pages)
        if not (1 <= self.max_pages <= 10):
            raise CloseSpider(
                f"Invalid `max_pages`: {self.max_pages}. Must be between 1 and 10."
            )

    def start_requests(self):
        """
        Generates the initial requests for each subreddit URL retrieved from the 'subreddit_list_gen.db' database.
        """
        settings = get_project_settings()
        database_path = settings.get("DB_PATH")
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        try:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='subreddits'"
            )
            table_exists = cursor.fetchone()
            if not table_exists:
                raise CloseSpider("Subreddits table is missing in the database.")

            cursor.execute("SELECT url FROM subreddits LIMIT 1")
            row = cursor.fetchone()
            if not row:
                raise CloseSpider(
                    "Subreddits table is empty, please populate it with URLs."
                )

            cursor.execute("SELECT url FROM subreddits")
            rows = cursor.fetchall()

            for row in rows:
                url = row[0]
                json_url = f"{url}.json?limit=100"
                yield Request(
                    url=json_url,
                    callback=self.parse,
                    meta={"start_url": url, "page": 1, "max_pages": self.max_pages},
                )
        except sqlite3.Error:
            raise CloseSpider("Database error encountered.")
        finally:
            connection.close()

    def parse(self, response):
        """
        Parses the JSON response and handles pagination.

        Args:
            response (scrapy.http.Response): The HTTP response object.
        """
        try:
            data = response.json()
        except JSONDecodeError:
            logging.error(f"Failed to decode JSON from {response.url}")
            return

        start_url = response.meta.get("start_url")
        current_page = response.meta.get("page", 1)
        max_pages = response.meta.get("max_pages", 1)

        posts = data.get("data", {}).get("children", [])
        num_posts = len(posts)

        for post in posts:
            post_data = post["data"]
            item = RedditPostItem(
                author=post_data.get("author"),
                comments=post_data.get("num_comments"),
                permalink=urljoin("https://www.reddit.com", post_data.get("permalink")),
                created_timestamp=post_data.get("created_utc"),
                upvotes=post_data.get("ups"),
                post_body=post_data.get("selftext"),
                post_title=post_data.get("title"),
                id=post_data.get("id"),
                edited=post_data.get("edited"),
                upvote_ratio=post_data.get("upvote_ratio"),
                subreddit_subscribers=post_data.get("subreddit_subscribers"),
            )
            yield item
        logging.info(
            f"Scraped {num_posts} posts from subreddit: {start_url} (Page {current_page})"
        )

        after = data.get("data", {}).get("after")
        if after and current_page < max_pages:
            next_page = current_page + 1
            next_json_url = f"{start_url}.json?after={after}&limit=100"
            yield Request(
                url=next_json_url,
                callback=self.parse,
                meta={
                    "start_url": start_url,
                    "page": next_page,
                    "max_pages": max_pages,
                },
            )
        elif after and current_page >= max_pages:
            logging.info(f"Reached max_pages={max_pages} for subreddit: {start_url}")
        else:
            logging.info(f"No more pages to scrape for subreddit: {start_url}")
