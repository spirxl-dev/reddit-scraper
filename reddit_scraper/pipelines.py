import os
import sqlite3
import logging
import json
from urllib.parse import urlparse
from datetime import datetime, timezone
from scrapy.utils.project import get_project_settings


class SubredditPostMetaPipeline:
    """
    Pipeline for storing `subreddit_post_meta` spider data in the SQLite database.
    """

    def open_spider(self, spider):
        settings = get_project_settings()

        db_dir = settings.get("DB_DIR")
        db_path = settings.get("DB_PATH")

        os.makedirs(db_dir, exist_ok=True)

        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_posts_table()

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()
        logging.info("Closed SQLite connection")

    def process_item(self, item, spider):
        item_dict = dict(item)

        item_dict["subreddit"] = self._extract_subreddit_from_permalink(
            item.get("permalink")
        )
        item_dict["created_timestamp"] = self._convert_timestamp(
            item.get("created_timestamp")
        )
        item_dict["edited"] = self._convert_timestamp(item.get("edited"))

        for key in item_dict:
            value = item_dict[key]
            if isinstance(value, (dict, list)):
                item_dict[key] = json.dumps(value)
            else:
                item_dict[key] = value

        self._insert_item(item_dict)
        logging.debug("Inserted item into posts table in SQLite database")

        return item

    def _create_posts_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            subreddit TEXT,
            author TEXT,
            created_timestamp REAL,
            post_title TEXT,
            post_body TEXT,
            permalink TEXT,
            upvotes INTEGER,
            upvote_ratio REAL,
            comments INTEGER,
            edited REAL,
            subreddit_subscribers INTEGER
        );
        """
        self.cursor.execute(create_table_sql)
        logging.info("Created 'posts' table in SQLite database")

    def _extract_subreddit_from_permalink(self, permalink):
        if not permalink:
            return None
        parsed_url = urlparse(permalink)
        path_parts = parsed_url.path.strip("/").split("/")
        if len(path_parts) >= 3 and path_parts[0].lower() == "r":
            return path_parts[1]
        return None

    def _insert_item(self, item_dict):
        columns = ", ".join(item_dict.keys())
        placeholders = ", ".join(["?"] * len(item_dict))
        insert_sql = f"INSERT OR REPLACE INTO posts ({columns}) VALUES ({placeholders})"

        try:
            self.cursor.execute(insert_sql, tuple(item_dict.values()))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error inserting item into posts table: {e}")

    def _convert_timestamp(self, timestamp):
        """
        Convert a timestamp (seconds since epoch) to ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ) format.

        """
        try:
            if timestamp == 0:
                return timestamp
            # Convert the timestamp to a timezone-aware datetime object
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            # Format the datetime object to ISO 8601 standard
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception as e:
            return f"Error: {e}"
