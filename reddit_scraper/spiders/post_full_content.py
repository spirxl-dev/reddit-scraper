import json
import os
from urllib.parse import urlparse, quote
from scrapy import Spider, Request
from scrapy_playwright.page import PageMethod
import logging


class PostFullContentSpider(Spider):
    name = "post_full_content"
    start_urls = [
        "https://www.reddit.com/r/ArtificialInteligence/comments/1g0v2bt/id_like_to_clone_my_dads_voice_how_can_i_do_that/",
        "https://www.reddit.com/r/unitedairlines/comments/1g0ptbq/help_with_flight_diverted/",
        "https://www.reddit.com/r/ProgrammerHumor/comments/1g2nr38/linkedinisfunnyattimes/",
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "domcontentloaded"),
                        PageMethod(
                            "evaluate", "window.scrollBy(0, window.innerHeight * 10);"
                        ),
                        PageMethod("wait_for_timeout", 2000),
                    ],
                },
            )

    def parse(self, response):
        if "playwright_page" in response.meta:

            post_data_element = response.xpath("//shreddit-post")
            post_id = post_data_element.xpath("./@id").get()
            post_title = post_data_element.xpath("./@post-title").get()
            post_content = " ".join(
                response.xpath(
                    '//div[@id="t3_1g0619n-post-rtjson-content"]//p//text()'
                ).getall()
            )
            post_score = int(post_data_element.xpath("./@score").get())
            post_permalink = post_data_element.xpath("./@permalink").get()
            post_created_timestamp = post_data_element.xpath("./@created-timestamp").get()
            post_comment_count = int(post_data_element.xpath("./@comment-count").get())
            post_author_name = post_data_element.xpath("./@author").get()
            post_subreddit = post_data_element.xpath("./@subreddit-prefixed-name").get()

            comment_tree = response.xpath("//shreddit-comment-tree")
            comments = []
            if comment_tree:
                comment_sections = comment_tree.xpath(".//shreddit-comment")
                for comment in comment_sections:
                    comment_author = comment.xpath(".//@author").get()
                    comment_id = comment.xpath(".//@thingid").get()
                    comment_permalink = comment.xpath(".//@permalink").get()
                    comment_post_id = comment.xpath(".//@postid").get()
                    comment_score = int(comment.xpath(".//@score").get(default=0))
                    comment_text = " ".join(comment.xpath(".//p//text()").getall())

                    comment_data = {
                        "comment_author": comment_author,
                        "comment_id": comment_id,
                        "permalink": comment_permalink,
                        "post_id": comment_post_id,
                        "score": int(comment_score),
                        "comment_text": comment_text.strip(),
                    }
                    comments.append(comment_data)

            post_data = {
                "post_id": post_id,
                "post_title": post_title,
                "post_content": post_content,
                "post_upvotes": post_score,
                "post_author": post_author_name,
                "post_comment_count": post_comment_count,
                "created_timestamp": post_created_timestamp,
                "permalink": post_permalink,
                "subreddit": post_subreddit,
                "comments": comments,
            }

            parsed_url = urlparse(response.url)
            post_path = parsed_url.path.replace("/", "_")
            safe_filename = quote(post_path, safe="")

            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, f"{safe_filename}.json")

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(post_data, f, ensure_ascii=False, indent=4)

            logging.info(f"Post data saved to {file_path}")

            response.meta["playwright_page"].close()

            yield post_data
        else:
            self.logger.error("playwright_page not found in response meta.")
