import scrapy


class RedditPostItem(scrapy.Item):
    # Basic post metadata
    title = scrapy.Field()
    author = scrapy.Field()
    created_timestamp = scrapy.Field()
    edited = scrapy.Field()
    permalink = scrapy.Field()
    subreddit = scrapy.Field()
    subreddit_subscribers = scrapy.Field()
    post_title = scrapy.Field()
    post_body = scrapy.Field()
    url = scrapy.Field()
    id = scrapy.Field()

    # Engagement metrics
    upvotes = scrapy.Field()
    upvote_ratio = scrapy.Field()
    comments = scrapy.Field()