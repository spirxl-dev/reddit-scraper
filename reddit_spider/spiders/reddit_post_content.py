from scrapy import Spider


class RedditPostContent(Spider):
    """
    A Scrapy spider that scrapes the full content of Reddit posts using the permalinks
    gathered by the reddit_post_metadata spider.

    The spider expects a list of permalinks and extracts details such as post body, comments, etc.
    """

    name = "reddit_post_content"

    allowed_domains = []
    start_urls = []

    def parse(self, response):
        pass
