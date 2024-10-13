import json
import os
from datetime import datetime
from urllib.parse import urlparse


class SubredditListGenSpiderPipeline:
    def open_spider(self, spider):
        self.subreddit_urls = []

    def close_spider(self, spider):
        with open("reddit_scraper/spiders/constants/start_urls.py", "w") as f:
            f.write(
                "# Automatically generated list of subreddit start URLs. Run the subreddit_list_gen spider to get started.;\n"
            )
            f.write("START_URLS = [\n")
            for url in self.subreddit_urls:
                f.write(f"    '{url}',\n")
            f.write("]\n")

    def process_item(self, item, spider):
        url = item.get("url")
        if url:
            self.subreddit_urls.append(url)
        return item


class SubredditPostMetaSpiderPipeline:
    def _format_timestamp(self, timestamp: str) -> str:
        try:
            parsed_time = datetime.fromisoformat(timestamp)
            return parsed_time.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            return timestamp

    def _generate_filename(self, url: str) -> str:
        parsed_url = urlparse(url)
        filename = f"{parsed_url.netloc}{parsed_url.path}".replace("/", "_") + ".json"
        return os.path.join(self.output_dir, filename)

    def open_spider(self, spider):
        self.output_dir = "json_files"
        os.makedirs(self.output_dir, exist_ok=True)
        self.files = {}

    def close_spider(self, spider):
        for file in self.files.values():
            file.seek(file.tell() - 2, os.SEEK_SET)
            file.write("\n]")
            file.close()

    def process_item(self, item, spider):
        if "created_timestamp" in item:
            item["created_timestamp"] = self._format_timestamp(
                item["created_timestamp"]
            )

        if "permalink" in item:
            item["permalink"] = f"https://www.reddit.com{item["permalink"]}"

        start_url = item.get("start_url")
        filename = self._generate_filename(start_url)

        if filename not in self.files:
            self.files[filename] = open(filename, "w", encoding="utf-8")
            self.files[filename].write("[\n")

        json.dump(dict(item), self.files[filename], ensure_ascii=False, indent=4)
        self.files[filename].write(",\n")

        return item
