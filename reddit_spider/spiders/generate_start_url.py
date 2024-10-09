from scrapy import Spider


class GenerateStartURL(Spider):
    """
    A Scrapy spider that scrapes the list of subreddits from the Reddit /subreddits page,
    to dynamically generate the 'START_URL' list object for scraping subreddit metadata.

    Variables can be configured to control the scraping behavior.
    """

    name = "generate_start_url"
    start_urls = ['https://www.reddit.com/subreddits/']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'ROBOTSTXT_OBEY': False
    }

    def parse(self, response):
        subreddits = response.css('div.sitetable div.entry')

        for subreddit in subreddits:
            title = subreddit.css('p.titlerow a.title::text').get()
            link = subreddit.css('p.titlerow a.title::attr(href)').get()
            subscribers = subreddit.css('span.number::text').get()

            yield {
                'title': title.strip() if title else None,
                'url': response.urljoin(link),
                'subscribers': subscribers.strip() if subscribers else None,
            }

        # Pagination - Follow the 'more' link to scrape additional pages
        next_page = response.css('a#sr-more-link::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
