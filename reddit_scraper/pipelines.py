import json
import os
import logging

class SubredditPostMetaPipeline:
    """Custom pipeline for subreddit_post_meta pipeline."""
    def open_spider(self, spider):
        self.data_folder = spider.data_folder
        self.files = {}
        self.subreddit_has_items = {}

    def close_spider(self, spider):
        for subreddit, file in self.files.items():
            file.write(']')
            file.close()
            logging.info(f"Closed JSON array in {file.name}")

    def process_item(self, item, spider):
        subreddit = item.get('subreddit') or spider.get_subreddit_name(item['start_url'])
        posts_filename = os.path.join(self.data_folder, f"{subreddit}_posts.json")

        if subreddit not in self.files:
            try:
                os.makedirs(self.data_folder, exist_ok=True)
                file = open(posts_filename, 'w', encoding='utf-8')
                file.write('[')
                self.files[subreddit] = file
                self.subreddit_has_items[subreddit] = False
                logging.info(f"Started new JSON array in {posts_filename}")
            except IOError as e:
                spider.logger.error(f"Error opening {posts_filename} for writing: {e}")
                return item

        file = self.files[subreddit]

        try:
            if self.subreddit_has_items[subreddit]:
                file.write(',\n')
            else:
                self.subreddit_has_items[subreddit] = True
            json.dump(dict(item), file)
            logging.debug(f"Appended item to {posts_filename}")
        except IOError as e:
            spider.logger.error(f"Error writing item to {posts_filename}: {e}")

        return item