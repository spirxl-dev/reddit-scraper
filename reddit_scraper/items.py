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
    post_id = scrapy.Field()

    # Engagement metrics
    upvotes = scrapy.Field()
    ups = scrapy.Field()
    score = scrapy.Field()
    upvote_ratio = scrapy.Field()
    comments = scrapy.Field()
    
    # Flair and appearance
    link_flair_text = scrapy.Field()

    # Media and preview information
    media = scrapy.Field()
    media_metadata = scrapy.Field()
    preview = scrapy.Field()
    thumbnail = scrapy.Field()
    thumbnail_width = scrapy.Field()
    thumbnail_height = scrapy.Field()
    gallery_data = scrapy.Field()