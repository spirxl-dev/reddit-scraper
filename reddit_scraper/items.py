# reddit_scraper/items.py

import scrapy


class RedditPostItem(scrapy.Item):
    post_title = scrapy.Field()
    author = scrapy.Field()
    comments = scrapy.Field()
    permalink = scrapy.Field()
    created_timestamp = scrapy.Field()
    start_url = scrapy.Field()
    post_content = scrapy.Field()
    post_body = scrapy.Field()
    upvotes = scrapy.Field()
