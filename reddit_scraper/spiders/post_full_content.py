from scrapy import Spider


class PostFullContentSpider(Spider):
    """
    A Scrapy spider that scrapes the full content of Reddit posts.

    This spider uses a list of permalinks gathered by the subreddit_post_meta spider
    to scrape the detailed content of individual posts. It extracts various details such as:
        - post body
        - comments
        - upvotes
        - additional metadata, if available

    """

    name = "post_full_content"

    allowed_domains = []
    start_urls = []

    def parse(self, response):
        pass
