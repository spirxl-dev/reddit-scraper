from scrapy import Spider, Request


class SubredditListGenSpider(Spider):
    """
    A Scrapy spider that saves subreddit URLs using Reddit's JSON API.

    This spider scrapes the Reddit /subreddits page in JSON format and saves each
    subreddit URL directly to an SQLite database. The stored URLs can be used as
    starting points for other spiders, such as subreddit_post_metadata, to enable
    further scraping of subreddit content.

    Example use from CLI:
        scrapy crawl subreddit_list_gen -a max_pages=3

    """

    name = "subreddit_list_gen"
    start_urls = ["https://www.reddit.com/subreddits.json"]

    custom_settings = {
        "ITEM_PIPELINES": {
            "reddit_scraper.pipelines.subreddit_list_gen_pipeline.SubredditListGenPipeline": 1,
        }
    }

    def __init__(self, max_pages=1, *args, **kwargs):
        """
        Initialises the spider with a maximum number of pages to scrape.

        Args:
            max_pages (int): The maximum number of pages (each page is a batch of approx 25 subreddit urls).
                             Defaults to 1.
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
            link = f"https://www.reddit.com{subreddit_data.get('url')}"

            yield {
                "url": link,
            }

        after = data.get("data", {}).get("after")
        if after:
            next_page = f"https://www.reddit.com/subreddits.json?after={after}"
            yield Request(next_page, callback=self.parse)

