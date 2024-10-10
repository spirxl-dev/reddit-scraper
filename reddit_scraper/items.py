# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RedditPostItem(scrapy.Item):
    start_url = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    comments = scrapy.Field()
    permalink = scrapy.Field()
    created_timestamp = scrapy.Field()
