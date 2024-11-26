from scrapy import Spider, Request
import logging


class PostFullContentSpider(Spider):
    """
    A Scrapy spider that fetches the content of an individual Reddit post.
    """

    name = "post_full_content"
    allowed_domains = ["reddit.com"]

    accounts = [
        {
            "client_id": "CLIENT_ID_1",
            "client_secret": "SECRET_1",
            "user_agent": "Agent_1",
            "username": "user1",
            "password": "pass1",
        },
        {
            "client_id": "CLIENT_ID_2",
            "client_secret": "SECRET_2",
            "user_agent": "Agent_2",
            "username": "user2",
            "password": "pass2",
        },
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "reddit_scraper.pipelines.post_full_content_pipeline.PostFullContentSpiderPipeline": 1,
        }
    }

    def start_requests(self):
        pass

    def parse(self, response):
        pass