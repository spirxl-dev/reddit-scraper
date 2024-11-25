from scrapy import Spider, Request
from scrapy_playwright.page import PageMethod
import logging


class PostFullContentSpider(Spider):
    """
    A Scrapy spider that scrapes the full content of an individual Reddit post.
    """

    name = "post_full_content"

    custom_settings = {
        "ITEM_PIPELINES": {
            "reddit_scraper.pipelines.PostFullContentSpiderPipeline": 1,
        }
    }

    def start_requests(self):
        pass

    def parse(self, response):
        pass