import logging
from json import JSONDecodeError
from urllib.parse import urljoin

from scrapy import Spider, Request

from reddit_scraper.items import RedditPostItem
from reddit_scraper.spiders.constants.start_urls import START_URLS


class SubredditPostMetaSpider(Spider):
    """
    A Scrapy spider that scrapes metadata from posts in multiple subreddits using Reddit's JSON endpoints.

    Example use from CLI:
        scrapy crawl subreddit_post_meta -a max_pages=10

    """

    name = "subreddit_post_meta"
    start_urls = START_URLS

    custom_settings = {
        "ITEM_PIPELINES": {
            "reddit_scraper.pipelines.SubredditPostMetaPipeline": 300,
        }
    }

    def __init__(self, max_pages=1, *args, **kwargs):
        """
        Initialises the spider with a maximum number of pages to scrape per subreddit.

        Args:
            max_pages (int): The maximum number of pages (each page is a batch of approx 100 posts) to scrape per subreddit.
                             Defaults to 1.
        """
        super(SubredditPostMetaSpider, self).__init__(*args, **kwargs)
        try:
            self.max_pages = int(max_pages)
            if self.max_pages < 1:
                raise ValueError
        except ValueError:
            logging.error("Invalid `max_pages` value. Should be a positive integer.")
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
                meta={"start_url": url, "page": 1, "max_pages": self.max_pages},
            )

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
                post_content=post_data.get("selftext_html"),
                post_title=post_data.get("title"),
                id=post_data.get("id"),
                name=post_data.get("name"),
                url=post_data.get("url"),
                score=post_data.get("score"),
                num_crossposts=post_data.get("num_crossposts"),
                over_18=post_data.get("over_18"),
                spoiler=post_data.get("spoiler"),
                locked=post_data.get("locked"),
                stickied=post_data.get("stickied"),
                distinguished=post_data.get("distinguished"),
                is_original_content=post_data.get("is_original_content"),
                is_self=post_data.get("is_self"),
                author_fullname=post_data.get("author_fullname"),
                author_premium=post_data.get("author_premium"),
                media=post_data.get("media"),
                media_metadata=post_data.get("media_metadata"),
                preview=post_data.get("preview"),
                thumbnail=post_data.get("thumbnail"),
                thumbnail_width=post_data.get("thumbnail_width"),
                thumbnail_height=post_data.get("thumbnail_height"),
                gallery_data=post_data.get("gallery_data"),
                created=post_data.get("created"),
                edited=post_data.get("edited"),
                ups=post_data.get("ups"),
                downs=post_data.get("downs"),
                upvote_ratio=post_data.get("upvote_ratio"),
                num_reports=post_data.get("num_reports"),
                link_flair_text=post_data.get("link_flair_text"),
                link_flair_css_class=post_data.get("link_flair_css_class"),
                post_hint=post_data.get("post_hint"),
                subreddit_subscribers=post_data.get("subreddit_subscribers"),
                selftext=post_data.get("selftext"),
                selftext_html=post_data.get("selftext_html"),
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
