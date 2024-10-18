from scrapy import Spider, Request


class SubredditListGenSpider(Spider):
    """
    A Scrapy spider that generates a list of subreddit URLs using Reddit's JSON API.

    This spider scrapes the Reddit /subreddits page (JSON format) to dynamically create the
    'START_URL' list for other spiders, such as subreddit_post_metadata.
    It collects URLs of subreddits, which can be used for further scraping.

    Configuration options are available to adjust scraping behavior.
    """

    name = "subreddit_list_gen"
    start_urls = ["https://www.reddit.com/subreddits.json"]

    custom_settings = {
        "ITEM_PIPELINES": {
            "reddit_scraper.pipelines.SubredditListGenSpiderPipeline": 1,
        }
    }

    def __init__(self, max_pages=3, *args, **kwargs):
        """
        Initialises the spider with a maximum number of pages to scrape.
        """
        super(SubredditListGenSpider, self).__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.page_count = 0

    def parse(self, response):
        if self.page_count >= self.max_pages:
            return

        self.page_count += 1
        data = response.json()

        subreddits = data.get("data", {}).get("children", [])

        for subreddit in subreddits:
            subreddit_data = subreddit.get("data", {})
            title = subreddit_data.get("display_name")
            link = f"https://www.reddit.com{subreddit_data.get('url')}"
            subscribers = subreddit_data.get("subscribers")

            yield {
                "title": title.strip() if title else None,
                "url": link,
                "subscribers": subscribers,
            }

        after = data.get("data", {}).get("after")
        if after:
            next_page = f"https://www.reddit.com/subreddits.json?after={after}"
            yield Request(next_page, callback=self.parse)


#  Example Usage: scrapy crawl subreddit_list_gen -a max_pages=3