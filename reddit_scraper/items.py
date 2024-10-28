import scrapy


class RedditPostItem(scrapy.Item):
    # Basic post metadata
    title = scrapy.Field()
    author = scrapy.Field()
    author_fullname = scrapy.Field()
    author_premium = scrapy.Field()
    created_timestamp = scrapy.Field()
    created = scrapy.Field()
    edited = scrapy.Field()
    permalink = scrapy.Field()
    subreddit = scrapy.Field()
    subreddit_subscribers = scrapy.Field()
    post_title = scrapy.Field()
    post_content = scrapy.Field()
    post_body = scrapy.Field()
    url = scrapy.Field()
    id = scrapy.Field()
    name = scrapy.Field()

    # Engagement metrics
    upvotes = scrapy.Field()
    ups = scrapy.Field()
    downs = scrapy.Field()
    score = scrapy.Field()
    upvote_ratio = scrapy.Field()
    num_reports = scrapy.Field()
    num_crossposts = scrapy.Field()
    comments = scrapy.Field()
    
    # Post attributes and status
    over_18 = scrapy.Field()
    spoiler = scrapy.Field()
    locked = scrapy.Field()
    stickied = scrapy.Field()
    distinguished = scrapy.Field()
    is_original_content = scrapy.Field()
    is_self = scrapy.Field()
    
    # Flair and appearance
    link_flair_text = scrapy.Field()
    link_flair_css_class = scrapy.Field()
    post_hint = scrapy.Field()

    # Media and preview information
    media = scrapy.Field()
    media_metadata = scrapy.Field()
    preview = scrapy.Field()
    thumbnail = scrapy.Field()
    thumbnail_width = scrapy.Field()
    thumbnail_height = scrapy.Field()
    gallery_data = scrapy.Field()

    # Text content
    selftext = scrapy.Field()
    selftext_html = scrapy.Field()