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
    A Scrapy spider for scraping metadata from posts in multiple subreddits using Reddit's JSON API.

    This spider fetches subreddit URLs from a SQLite database and scrapes post data
    (e.g., author, title, score, comments, etc.) using Reddit's JSON API endpoint.

    Example usage from CLI:
        scrapy crawl subreddit_post_meta -a max_pages=10
    """

    name = "subreddit_post_meta"

    custom_settings = {
        "ITEM_PIPELINES": {
            "reddit_scraper.pipelines.subreddit_post_meta_pipeline.SubredditPostMetaPipeline": 1,
        }
    }

    def __init__(self, max_pages=1, *args, **kwargs):
        """
        Initialises the spider with max_pages to scrape per subreddit.

        Args:
            max_pages (int): The maximum number of pages (each page is a batch of approx 100 posts) to scrape per subreddit.
                             Defaults to 1 page.
        """
        super(SubredditPostMetaSpider, self).__init__(*args, **kwargs)
        try:
            self.max_pages = int(max_pages)
            if self.max_pages < 1:
                raise ValueError
        except ValueError:
            logging.error(
                "Invalid `max_pages` value. Must be a positive integer. Defaulting to 1."
            )
            self.max_pages = 1

    def start_requests(self):
        """
        Generates initial HTTP requests for each subreddit URL stored in the SQLite database.

        This method:
        - Connects to the SQLite database defined in the project settings.
        - Ensures the 'subreddits' table exists and contains subreddit URLs.
        - Retrieves subreddit URLs and generates requests for their JSON endpoints.
        """
        settings = get_project_settings()
        database_path = settings.get("DB_PATH")

        try:
            connection = sqlite3.connect(database_path)
            cursor = connection.cursor()

            # Check if the 'subreddits' table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='subreddits'"
            )
            table_exists = cursor.fetchone()
            if not table_exists:
                raise CloseSpider("Subreddits table is missing in the database.")

            # Check if the 'subreddits' table contains any data
            cursor.execute("SELECT url FROM subreddits LIMIT 1")
            row = cursor.fetchone()
            if not row:
                raise CloseSpider(
                    "Subreddits table is empty. Populate it with subreddit URLs."
                )

            # Retrieve all subreddit URLs and generate initial requests
            cursor.execute("SELECT url FROM subreddits")
            rows = cursor.fetchall()

            for row in rows:
                url = row[0]
                json_url = url
                yield Request(
                    url=json_url,
                    callback=self.parse,
                    meta={"start_url": url, "page": 1, "max_pages": self.max_pages},
                )
        except sqlite3.Error:
            raise CloseSpider(
                "Database error encountered while accessing subreddit URLs."
            )
        finally:
            connection.close()

    def parse(self, response):
        """
        Parses the JSON response from the Reddit API and extracts post metadata.

        This method:
        - Decodes the JSON response and retrieves post data.
        - Yields post data as `RedditPostItem` objects.
        - Handles pagination by recursively requesting the next batch of posts (if available and within `max_pages`).

        Args:
            response (scrapy.http.Response): The HTTP response object containing subreddit JSON data.
        """
        try:
            data = response.json()
        except JSONDecodeError:
            logging.error(f"Failed to decode JSON from {response.url}")
            return

        start_url = response.meta.get("start_url")
        current_page = response.meta.get("page", 1)
        max_pages = response.meta.get("max_pages", 1)

        # Extract posts from the JSON response
        posts = data.get("data", {}).get("children", [])
        num_posts = len(posts)

        if num_posts == 0:
            logging.warning(
                f"No posts found in subreddit: {start_url} (Page {current_page})"
            )
            return

        # Process and yield post items
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
                post_id=post_data.get("id"),
                url=post_data.get("url"),
                score=post_data.get("score"),
                media=post_data.get("media"),
                media_metadata=post_data.get("media_metadata"),
                preview=post_data.get("preview"),
                thumbnail=post_data.get("thumbnail"),
                thumbnail_width=post_data.get("thumbnail_width"),
                thumbnail_height=post_data.get("thumbnail_height"),
                gallery_data=post_data.get("gallery_data"),
                edited=post_data.get("edited"),
                ups=post_data.get("ups"),
                upvote_ratio=post_data.get("upvote_ratio"),
                link_flair_text=post_data.get("link_flair_text"),
                subreddit_subscribers=post_data.get("subreddit_subscribers"),
            )
            yield item

        logging.info(
            f"Scraped {num_posts} posts from subreddit: {start_url} (Page {current_page})"
        )

        # Handle pagination if 'after' token is provided and max pages not exceeded
        after = data.get("data", {}).get("after")
        if after and current_page < max_pages:
            next_page = current_page + 1

            # Correctly construct the pagination URL
            if ".json?limit=100" in start_url:
                next_json_url = f"{start_url}&after={after}"
            else:
                next_json_url = f"{start_url}/.json?after={after}&limit=100"

            logging.info(
                f"Fetching next page for subreddit: {start_url} (Page {next_page})"
            )

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
