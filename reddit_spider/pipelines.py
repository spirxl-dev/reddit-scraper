import json
import os
from datetime import datetime, timezone
from urllib.parse import urlparse


class RedditSpiderPipeline:
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
            item["created_timestamp"] = self.format_timestamp(item["created_timestamp"])

        if "comments" in item:
            item["comments"] = self.convert_comments(item["comments"])

        start_url = item.get("start_url")
        filename = self.generate_filename(start_url)

        if filename not in self.files:
            self.files[filename] = open(filename, "w", encoding="utf-8")
            self.files[filename].write("[\n")

        json.dump(dict(item), self.files[filename], ensure_ascii=False, indent=4)
        self.files[filename].write(",\n")

        return item

    def format_timestamp(self, timestamp: str) -> str:
        try:
            parsed_time = datetime.fromisoformat(timestamp)
            return parsed_time.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            return timestamp

    def convert_comments(self, comments: str) -> int:
        try:
            return int(comments)
        except ValueError:
            return 0

    def generate_filename(self, url: str) -> str:
        parsed_url = urlparse(url)
        filename = f"{parsed_url.netloc}{parsed_url.path}".replace("/", "_") + ".json"
        return os.path.join(self.output_dir, filename)
