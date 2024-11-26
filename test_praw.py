import scrapy
import praw
from prawcore.exceptions import RequestException
from itertools import cycle


class RedditSpider(scrapy.Spider):
    name = "reddit_comments"
    allowed_domains = ["reddit.com"]

    # Replace with your Reddit accounts
    accounts = [
        {"client_id": "CLIENT_ID_1", "client_secret": "SECRET_1", "user_agent": "Agent_1", "username": "user1", "password": "pass1"},
        {"client_id": "CLIENT_ID_2", "client_secret": "SECRET_2", "user_agent": "Agent_2", "username": "user2", "password": "pass2"},
    ]

    def __init__(self, post_ids=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_ids = post_ids.split(",") if post_ids else []  # Pass post IDs as a comma-separated argument
        self.reddit_instances = [self.get_reddit_instance(**account) for account in self.accounts]
        self.reddit_cycle = cycle(self.reddit_instances)  # Rotate accounts

    def get_reddit_instance(self, client_id, client_secret, user_agent, username, password):
        return praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            username=username,
            password=password
        )

    def start_requests(self):
        for post_id in self.post_ids:
            yield scrapy.Request(
                url=f"https://reddit.com/{post_id}",
                callback=self.fetch_comments,
                cb_kwargs={"post_id": post_id},
                dont_filter=True
            )

    def parse(self, response, post_id):
        reddit = next(self.reddit_cycle)  # Rotate Reddit instances to share the load
        try:
            submission = reddit.submission(id=post_id)
            submission.comments.replace_more(limit=None)  # Expand all comments
            for comment in submission.comments.list():
                yield {
                    "comment_id": comment.id,
                    "post_id": post_id,
                    "parent_id": comment.parent_id,
                    "subreddit": comment.subreddit.display_name,
                    "author": str(comment.author) if comment.author else None,
                    "created_timestamp": comment.created_utc,
                    "comment_body": comment.body,
                    "permalink": f"https://reddit.com{comment.permalink}",
                    "upvotes": comment.ups,
                    "score": comment.score,
                    "edited": comment.edited if isinstance(comment.edited, bool) else None,
                    "depth": comment.depth
                }
        except RequestException as e:
            self.logger.error(f"Error fetching comments for post {post_id}: {e}")