# import json
# import os
# from datetime import datetime
# from urllib.parse import urlparse


# def _convert_to_int(value):
#     try:
#         return int(value)
#     except (ValueError, TypeError):
#         return None


# def _format_timestamp(timestamp: str) -> str:
#     try:
#         parsed_time = datetime.fromisoformat(timestamp)
#         return parsed_time.strftime("%Y-%m-%d %H:%M:%S")
#     except Exception:
#         return timestamp


# def _generate_filename(url: str, output_dir: str) -> str:
#     parsed_url = urlparse(url)
#     filename = f"{parsed_url.netloc}{parsed_url.path}".replace("/", "_") + ".json"
#     return os.path.join(output_dir, filename)


# class SubredditListGenSpiderPipeline:
#     """
#     Pipeline for subreddit_list_gen spider.
#     """

#     def open_spider(self, spider):
#         self.subreddit_urls = []

#     def close_spider(self, spider):
#         with open("reddit_scraper/spiders/constants/start_urls.py", "w") as f:
#             f.write(
#                 "# Automatically generated list of subreddit start URLs. Run the subreddit_list_gen spider to get started.\n"
#             )
#             f.write("START_URLS = [\n")
#             for url in self.subreddit_urls:
#                 f.write(f"    '{url}',\n")
#             f.write("]\n")

#     def process_item(self, item, spider):
#         url = item.get("url")
#         if url:
#             self.subreddit_urls.append(url)
#         return item


# class SubredditPostMetaSpiderPipeline:
#     """
#     Pipeline for subreddit_post_meta spider.
#     """

#     def open_spider(self, spider):
#         self.output_dir = "subreddit_post_meta_files"
#         os.makedirs(self.output_dir, exist_ok=True)
#         self.files = {}

#     def close_spider(self, spider):
#         for file in self.files.values():
#             file.seek(file.tell() - 2, os.SEEK_SET)
#             file.write("\n]")
#             file.close()

#     def process_item(self, item, spider):

#         if "created_timestamp" in item:
#             item["created_timestamp"] = _format_timestamp(item["created_timestamp"])

#         if "comments" in item:
#             item["comments"] = _convert_to_int(item["comments"])

#         if "permalink" in item:
#             item["permalink"] = f"https://www.reddit.com{item['permalink']}"

#         start_url = item.get("start_url")
#         filename = _generate_filename(start_url, self.output_dir)

#         if filename not in self.files:
#             self.files[filename] = open(filename, "w", encoding="utf-8")
#             self.files[filename].write("[\n")

#         json.dump(dict(item), self.files[filename], ensure_ascii=False, indent=4)
#         self.files[filename].write(",\n")

#         return item


# class PostFullContentSpiderPipeline:
#     """
#     Pipeline for post_full_content spider.
#     """

#     def open_spider(self, spider):
#         self.output_dir = "post_full_content_json_files"
#         os.makedirs(self.output_dir, exist_ok=True)
#         self.files = {}

#     def close_spider(self, spider):
#         for file in self.files.values():
#             file.seek(file.tell() - 2, os.SEEK_SET)
#             file.write("\n]")
#             file.close()

#     def process_item(self, item, spider):

#         if "post_upvotes" in item:
#             item["post_upvotes"] = _convert_to_int(item["post_upvotes"])

#         if "post_comment_count" in item:
#             item["post_comment_count"] = _convert_to_int(item["post_comment_count"])

#         if "post_permalink" in item:
#             item["post_permalink"] = f"https://www.reddit.com{item['post_permalink']}"
        
#         if "post_subreddit" in item:
#             item["post_subreddit"] = item["post_subreddit"].strip('r/')

#         if "comments" in item:
#             for comment in item["comments"]:
#                 if "comment_upvotes" in comment:
#                     comment["comment_upvotes"] = _convert_to_int(
#                         comment["comment_upvotes"]
#                     )
#                 if "comment_permalink" in comment:
#                     comment["comment_permalink"] = (
#                         f"https://www.reddit.com{comment['comment_permalink']}"
#                     )

#         start_url = item.get("start_url", item.get("post_permalink"))
#         filename = _generate_filename(start_url, self.output_dir)

#         if filename not in self.files:
#             self.files[filename] = open(filename, "w", encoding="utf-8")
#             self.files[filename].write("[\n")

#         json.dump(dict(item), self.files[filename], ensure_ascii=False, indent=4)
#         self.files[filename].write(",\n")

#         return item
