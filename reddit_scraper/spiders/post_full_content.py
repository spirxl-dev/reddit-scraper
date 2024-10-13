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
        "https://www.reddit.com/r/ProgrammerHumor/comments/1g2nr38/linkedinisfunnyattimes/"
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
                        PageMethod("evaluate", "window.scrollBy(0, window.innerHeight * 10);"),
                        PageMethod("wait_for_timeout", 2000),
                    ],
                    "start_url": url  # Pass the start URL into the request meta
                },
            )

    def parse(self, response):
        if "playwright_page" in response.meta:
            # Extract the start URL from meta
            start_url = response.meta.get("start_url")

            # Extract post details
            post_title = response.css("h1._eYtD2XCVieq6emjKBH3m::text").get()
            post_content = response.css("div[data-test-id='post-content'] p::text").getall()
            upvotes = response.css("div[data-test-id='upvote-button']::attr(aria-label)").get()
            post_author = response.xpath('//a[@aria-label]/text()').get()

            # Extract comment-count from shreddit-post-overflow-menu
            comment_count = response.xpath('//shreddit-post-overflow-menu/@comment-count').get()

            # Find the shreddit-comment-tree
            comment_tree = response.xpath('//shreddit-comment-tree')
            
            if not comment_tree:
                logging.warning(f"No comment tree found for post: {response.url}")
                return
            
            # Extract all shreddit-comment elements within the shreddit-comment-tree
            comments = []
            comment_sections = comment_tree.xpath('.//shreddit-comment')

            for comment in comment_sections:
                comment_author = comment.xpath('.//@author').get()
                comment_id = comment.xpath('.//@thingid').get()
                permalink = comment.xpath('.//@permalink').get()
                post_id = comment.xpath('.//@postid').get()
                score = comment.xpath('.//@score').get(default='0')
                comment_text = " ".join(comment.xpath('.//p//text()').getall())
                
                comment_data = {
                    "comment_author": comment_author,
                    "comment_id": comment_id,
                    "permalink": permalink,
                    "post_id": post_id,
                    "score": int(score),
                    "comment_text": comment_text.strip(),
                }
                comments.append(comment_data)

            # Create nested JSON structure for the post and associated metadata
            post_data = {
                "post_title": post_title,
                "post_content": post_content,
                "post_upvotes": upvotes,
                "post_author": post_author,
                "comment_count": comment_count,  # Add comment count
                "start_url": start_url,          # Add start URL
                "comments": comments
            }

            # Create a unique filename based on the post URL
            parsed_url = urlparse(response.url)
            post_path = parsed_url.path.replace('/', '_')
            safe_filename = quote(post_path, safe="")

            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, f"{safe_filename}.json")

            # Save the JSON data to a file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(post_data, f, ensure_ascii=False, indent=4)

            logging.info(f"Post data saved to {file_path}")

            # Close the Playwright page
            response.meta["playwright_page"].close()

            yield post_data
        else:
            self.logger.error("playwright_page not found in response meta.")