from pprint import pprint
from scrapy import Spider, Request
import sqlite3
from scrapy.exceptions import CloseSpider
from scrapy.utils.project import get_project_settings


class PostFullContentSpider(Spider):
    """
    A Scrapy spider that fetches the content of an individual Reddit post using PRAW.
    """

    name = "post_full_content"

    custom_settings = {
        "ITEM_PIPELINES": {
            "reddit_scraper.pipelines.post_full_content_pipeline.PostFullContentSpiderPipeline": 1,
        }
    }

    accounts = [
        {
            "client_id": "CLIENT_ID_1",
            "client_secret": "SECRET_1",
            "user_agent": "Agent_1",
            "username": "user1",
            "password": "pass1",
        },
        {
            "client_id": "CLIENT_ID_2",
            "client_secret": "SECRET_2",
            "user_agent": "Agent_2",
            "username": "user2",
            "password": "pass2",
        },
    ]

    def start_requests(self):
        settings = get_project_settings()
        database_path = settings.get("DB_PATH")

        try:
            connection = sqlite3.connect(database_path)
            cursor = connection.cursor()

            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='comments'"
            )
            table_exists = cursor.fetchone()

            if not table_exists:
                raise CloseSpider("comments table is missing in the database.")

            cursor.execute("SELECT post_id FROM comments LIMIT 1")
            row = cursor.fetchone()
            if not row:
                raise CloseSpider("comments table is empty, please populate it.")

            cursor.execute("SELECT url FROM comments")
            post_ids: list = cursor.fetchall()
            pprint(post_ids)

        except sqlite3.Error:
            raise CloseSpider("Database error encountered.")
        finally:
            connection.close()

    def parse(self, response):
        pass
