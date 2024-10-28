import json
import os
import logging
from urllib.parse import urlparse


class SubredditPostMetaPipeline:
    """Custom pipeline for subreddit_post_meta pipeline."""

    def open_spider(self, spider):
        self.data_folder = spider.data_folder
        self.files = {}
        self.subreddit_has_items = {}
        self.spider = spider

    def close_spider(self, spider):
        for subreddit, file in self.files.items():
            file.write("]")
            file.close()
            logging.info(f"Closed JSON array in {file.name}")

    def process_item(self, item, spider):
        permalink = item.get("permalink")
        subreddit = self.extract_subreddit_from_permalink(permalink)
        if not subreddit:
            spider.logger.error("Subreddit not found in item permalink")
            return item

        posts_filename = os.path.join(self.data_folder, f"{subreddit}_posts.json")

        if subreddit not in self.files:
            try:
                os.makedirs(self.data_folder, exist_ok=True)
                file = open(posts_filename, "w", encoding="utf-8")
                file.write("[")
                self.files[subreddit] = file
                self.subreddit_has_items[subreddit] = False
                logging.info(f"Started new JSON array in {posts_filename}")
            except IOError as e:
                spider.logger.error(f"Error opening {posts_filename} for writing: {e}")
                return item

        file = self.files[subreddit]

        try:
            if self.subreddit_has_items[subreddit]:
                file.write(",\n")
            else:
                self.subreddit_has_items[subreddit] = True

            item_dict = dict(item)

            def serialize(value):
                try:
                    json.dumps(value)
                    return value
                except TypeError:
                    if isinstance(value, dict):
                        return {k: serialize(v) for k, v in value.items()}
                    elif isinstance(value, list):
                        return [serialize(v) for v in value]
                    else:
                        return str(value)

            for key, value in item_dict.items():
                if isinstance(value, (dict, list)):
                    item_dict[key] = serialize(value)

            json.dump(item_dict, file)
            logging.debug(f"Appended item to {posts_filename}")
        except Exception as e:
            spider.logger.error(f"Error writing item to {posts_filename}: {e}")

        return item

    def extract_subreddit_from_permalink(self, permalink):
        """
        Extracts the subreddit name from the given permalink URL.

        Args:
            permalink (str): The permalink URL of the Reddit post.

        Returns:
            str: The subreddit name or None if it cannot be extracted.
        """
        if not permalink:
            return None
        parsed_url = urlparse(permalink)
        path_parts = parsed_url.path.strip("/").split("/")
        if len(path_parts) >= 3 and path_parts[0].lower() == "r":
            return path_parts[1]
        return None
