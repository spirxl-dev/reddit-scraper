from scrapy import Spider


class RedditSubredditListSpider(Spider):
    """
    A Scrapy spider that generates a list of subreddit URLs.

    This spider scrapes the Reddit /subreddits page to dynamically create the
    'START_URL' list for other spiders, such as subreddit_post_metadata.
    It collects URLs of subreddits, which can be used for further scraping.

    Configuration options will be available to adjust scraping behavior.
    """

    name = "subreddit_list_gen"
    start_urls = ["https://www.reddit.com/subreddits/"]

    custom_settings = {
        "ITEM_PIPELINES": {
            "reddit_scraper.pipelines.SubredditListGenSpiderPipeline": 1,
        }
    }

    def __init__(self, max_pages=3, *args, **kwargs):
        """
        Initializes the spider with a maximum number of pages to scrape.
        """
        super(RedditSubredditListSpider, self).__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.page_count = 0

    def parse(self, response):
        if self.page_count >= self.max_pages:
            return

        self.page_count += 1
        subreddits = response.css("div.sitetable div.entry")

        for subreddit in subreddits:
            title = subreddit.css("p.titlerow a.title::text").get()
            link = subreddit.css("p.titlerow a.title::attr(href)").get()
            subscribers = subreddit.css("span.number::text").get()

            yield {
                "title": title.strip() if title else None,
                "url": response.urljoin(link),
                "subscribers": subscribers.strip() if subscribers else None,
            }

        # Pagination - Follow the 'more' link to scrape additional pages
        next_page = response.css("a#sr-more-link::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

#  Example Usage: scrapy crawl subreddit_list_gen -a max_pages=3