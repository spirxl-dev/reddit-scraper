import os
import sqlite3
import logging
from scrapy.utils.project import get_project_settings


class PostFullContentSpiderPipeline:
    """
    Pipeline for storing `post_full_content` spider data in the SQLite database.
    """

    def open_spider(self, spider):
        settings = get_project_settings()

        db_dir = settings.get("DB_DIR")
        db_path = settings.get("DB_PATH")

        os.makedirs(db_dir, exist_ok=True)

        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_comments_table()

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()
        logging.info("Closed SQLite connection")

    def process_item(self, item, spider):
        pass

    def _create_comments_table(self):
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS comments (
                id TEXT PRIMARY KEY,
                post_id TEXT,
                body TEXT,
                author TEXT,
                FOREIGN KEY (post_id) REFERENCES posts (id)
            );
            """
        self.cursor.execute(create_table_sql)
        logging.info("Created 'comments' table in SQLite database")
