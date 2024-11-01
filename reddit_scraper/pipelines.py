import os
import sqlite3
import logging
import json
from urllib.parse import urlparse
from scrapy.utils.project import get_project_settings


class SubredditPostMetaPipeline:
    """
    Pipeline for storing subreddit_post_meta spider data in an SQLite database.

    Inserts each item into a 'posts' table with a 'subreddit' column to distinguish
    posts from different subreddits.
    """

    def open_spider(self, spider):
        settings = get_project_settings()
        databases_dir = settings.get("DB_DIR")
        database_path = settings.get("SUBREDDIT_POST_META_DB_PATH")

        os.makedirs(databases_dir, exist_ok=True)

        self.conn = sqlite3.connect(database_path)
        self.cursor = self.conn.cursor()
        self.create_posts_table()

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()
        logging.info(f"Closed SQLite database")

    def process_item(self, item, spider):
        item_dict = dict(item)
        item_dict["subreddit"] = self._extract_subreddit_from_permalink(
            item.get("permalink")
        )

        for key in item_dict:
            value = item_dict[key]
            if isinstance(value, (dict, list)):
                item_dict[key] = json.dumps(value)
            else:
                item_dict[key] = value

        self.insert_item(item_dict)
        logging.debug(f"Inserted item into posts table in SQLite database")

        return item

    def create_posts_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            subreddit TEXT,
            name TEXT,
            author TEXT,
            author_fullname TEXT,
            author_premium BOOLEAN,
            created_timestamp REAL,
            upvotes INTEGER,
            comments INTEGER,
            permalink TEXT,
            post_body TEXT,
            post_content TEXT,
            post_title TEXT,
            url TEXT,
            score INTEGER,
            num_crossposts INTEGER,
            over_18 BOOLEAN,
            spoiler BOOLEAN,
            locked BOOLEAN,
            stickied BOOLEAN,
            distinguished TEXT,
            is_original_content BOOLEAN,
            is_self BOOLEAN,
            media TEXT,
            media_metadata TEXT,
            preview JSON,
            thumbnail TEXT,
            thumbnail_width INTEGER,
            thumbnail_height INTEGER,
            gallery_data TEXT,
            created REAL,
            edited BOOLEAN,
            ups INTEGER,
            downs INTEGER,
            upvote_ratio REAL,
            num_reports INTEGER,
            link_flair_text TEXT,
            link_flair_css_class TEXT,
            post_hint TEXT,
            subreddit_subscribers INTEGER,
            selftext TEXT,
            selftext_html TEXT
        );
        """
        self.cursor.execute(create_table_sql)
        logging.info("Created posts table in SQLite database")

    def insert_item(self, item_dict):
        """Inserts an item into the posts table"""
        columns = ", ".join(item_dict.keys())
        placeholders = ", ".join(["?"] * len(item_dict))
        insert_sql = f"INSERT OR REPLACE INTO posts ({columns}) VALUES ({placeholders})"

        try:
            self.cursor.execute(insert_sql, tuple(item_dict.values()))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error inserting item into posts table: {e}")

    def _extract_subreddit_from_permalink(self, permalink):
        """Extracts the subreddit name from the given permalink URL"""
        if not permalink:
            return None
        parsed_url = urlparse(permalink)
        path_parts = parsed_url.path.strip("/").split("/")
        if len(path_parts) >= 3 and path_parts[0].lower() == "r":
            return path_parts[1]
        return None
