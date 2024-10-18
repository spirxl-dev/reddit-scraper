from scrapy import Spider, Request
# from reddit_scraper.items import RedditPostItem  # Assuming you still have this defined
from reddit_scraper.spiders.constants.start_urls import START_URLS
import logging
import json
import os
from urllib.parse import urljoin, urlparse


class SubredditPostMetaSpider(Spider):
    """
    A Scrapy spider that scrapes metadata from posts in multiple subreddits using Reddit's JSON endpoints.

    Example use from CLI: 
        scrapy crawl subreddit_post_meta -a max_pages=10

    Features:
        - Scrapes up to `max_pages` (default: 1) pages of posts per subreddit.
        - Saves extracted post data to JSON files in a specified folder.
        - Logs the exit IP address, user-agent, and proxy information.
        - Logs and prints the number of posts scraped per subreddit.
    """

    name = "subreddit_post_meta"
    start_urls = START_URLS

    # custom_settings = {
    #     "ITEM_PIPELINES": {
    #         "reddit_scraper.pipelines.SubredditPostMetaSpiderPipeline": 1,
    #     }
    # }

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

        # Specify the folder where you want to save the data
        self.data_folder = "data"  # You can change 'data' to any folder name you prefer
        os.makedirs(self.data_folder, exist_ok=True)

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

        start_url = response.meta.get("start_url")
        current_page = response.meta.get("page", 1)
        max_pages = response.meta.get("max_pages", 1)

        posts = data.get("data", {}).get("children", [])
        num_posts = len(posts)

        extracted_posts = []
        for post in posts:
            post_data = post["data"]
            item = {
                "title": post_data.get("title"),
                "author": post_data.get("author"),
                "comments": post_data.get("num_comments"),
                "permalink": urljoin("https://www.reddit.com", post_data.get("permalink")),
                "created_timestamp": post_data.get("created_utc"),
                "start_url": start_url
            }
            extracted_posts.append(item)

        logging.info(f"Scraped {num_posts} posts from subreddit: {start_url} (Page {current_page})")

        subreddit_name = self.get_subreddit_name(start_url)
        posts_filename = os.path.join(self.data_folder, f"{subreddit_name}_posts.json")

        try:
            with open(posts_filename, "a", encoding='utf-8') as posts_file:
                for post in extracted_posts:
                    json.dump(post, posts_file)
                    posts_file.write("\n")
            logging.info(f"Appended extracted post data to {posts_filename}")
        except IOError as e:
            self.logger.error(f"Error saving extracted post data to {posts_filename}: {e}")

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