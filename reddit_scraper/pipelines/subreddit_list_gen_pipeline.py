import os
import sqlite3
import logging
from scrapy.utils.project import get_project_settings


class SubredditListGenPipeline:
    """
    Pipeline for storing scraped subreddit URLs from `subreddit_list_gen` spider in the SQLite database.
    """

    def open_spider(self, spider):
        settings = get_project_settings()
        db_dir = settings.get("DB_DIR")
        db_path = settings.get("DB_PATH")

        os.makedirs(db_dir, exist_ok=True)

        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_subreddits_table()

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()
        logging.info(f"Closed SQLite connection")

    def _create_subreddits_table(self):
        """Creates the subreddits table if it doesn't already exist."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS subreddits (
            url TEXT PRIMARY KEY
        );
        """
        self.cursor.execute(create_table_sql)
        logging.info("Created `subreddits` table in SQLite database")
