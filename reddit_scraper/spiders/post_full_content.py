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

    custom_settings = {
        "ITEM_PIPELINES": {
            "reddit_scraper.pipelines.PostFullContentSpiderPipeline": 1,
        }
    }

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

    async def parse(self, response):
        if "playwright_page" in response.meta:

            post_data_element = response.xpath("//shreddit-post")
            if not post_data_element:
                logging.warning(
                    f"No <shreddit-post> element found for URL: {response.url}"
                )
                return

            post_id = post_data_element.xpath("./@id").get()
            post_title = post_data_element.xpath("./@post-title").get()

            post_content_element_id = f"//div[@id='{post_id}-post-rtjson-content']"
            post_content_elements = response.xpath(post_content_element_id)

            if not post_content_elements:
                post_content = "No post content available"
            else:
                post_content = " ".join(
                    post_content_elements.xpath(".//p//text()").getall()
                )

            post_permalink = post_data_element.xpath("./@permalink").get()
            post_created_timestamp = post_data_element.xpath(
                "./@created-timestamp"
            ).get()
            post_upvotes = post_data_element.xpath("./@score").get()
            post_comment_count = post_data_element.xpath("./@comment-count").get()
            post_author = post_data_element.xpath("./@author").get()
            post_subreddit = post_data_element.xpath("./@subreddit-prefixed-name").get()
            post_item_state = post_data_element.xpath("./@item-state").get()

            comment_tree = response.xpath("//shreddit-comment-tree")
            comments = []
            if comment_tree:
                comment_sections = comment_tree.xpath(".//shreddit-comment")
                for comment in comment_sections:
                    comment_author = comment.xpath(".//@author").get()
                    comment_id = comment.xpath(".//@thingid").get()
                    comment_permalink = comment.xpath(".//@permalink").get()
                    comment_post_id = comment.xpath(".//@postid").get()
                    comment_upvotes = comment.xpath(".//@score").get(default="0")
                    comment_text = " ".join(comment.xpath(".//p//text()").getall())

                    comment_data = {
                        "comment_author": comment_author,
                        "comment_id": comment_id,
                        "comment_permalink": comment_permalink,
                        "comment_post_id": comment_post_id,
                        "comment_upvotes": comment_upvotes,
                        "comment_text": comment_text.strip(),
                    }
                    comments.append(comment_data)

            post_data = {
                "post_id": post_id,
                "post_title": post_title,
                "post_content": post_content,
                "post_upvotes": post_upvotes,
                "post_author": post_author,
                "post_created_timestamp": post_created_timestamp,
                "post_comment_count": post_comment_count,
                "post_permalink": post_permalink,
                "post_subreddit": post_subreddit,
                "post_item_state": post_item_state,
                "comments": comments,
            }

            await response.meta["playwright_page"].close()

            yield post_data
        else:
            self.logger.error("playwright_page not found in response meta.")
