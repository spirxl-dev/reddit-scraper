# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


import scrapy

class RedditPostItem(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    comments = scrapy.Field()
    permalink = scrapy.Field()
    created_timestamp = scrapy.Field()
    start_url = scrapy.Field()

    post_title = scrapy.Field()
    post_content = scrapy.Field()
    post_body = scrapy.Field()
    upvotes = scrapy.Field()
