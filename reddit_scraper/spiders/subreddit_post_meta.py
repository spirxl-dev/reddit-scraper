import sqlite3
import json
import requests
import logging
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO)

# Database configuration
DATABASE_PATH = "database/data.db"
SUBREDDIT_TABLE = "subreddits"
POSTS_TABLE = "posts"

# Scraping configuration
POSTS_PER_PAGE = 100


def setup_database():
    """
    Set up the SQLite database with the required tables.
    """
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    # Create subreddits table
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {SUBREDDIT_TABLE} (
            id INTEGER PRIMARY KEY,
            url TEXT NOT NULL UNIQUE
        )
        """
    )

    # Create posts table
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {POSTS_TABLE} (
            post_id TEXT PRIMARY KEY,
            subreddit TEXT,
            author TEXT,
            created_timestamp REAL,
            post_title TEXT,
            post_body TEXT,
            url TEXT,
            permalink TEXT,
            upvotes INTEGER,
            score INTEGER,
            upvote_ratio REAL,
            ups INTEGER,
            comments INTEGER,
            link_flair_text TEXT,
            thumbnail TEXT,
            thumbnail_width INTEGER,
            thumbnail_height INTEGER,
            preview TEXT,
            media_metadata TEXT,
            gallery_data TEXT,
            edited REAL,
            subreddit_subscribers INTEGER
        )
        """
    )

    connection.commit()
    connection.close()


def get_subreddit_urls():
    """
    Retrieve subreddit URLs from the database.

    Returns:
        list: A list of subreddit URLs.
    """
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    try:
        cursor.execute(f"SELECT url FROM {SUBREDDIT_TABLE}")
        urls = [row[0] for row in cursor.fetchall()]
        return urls
    except sqlite3.Error as e:
        logging.error(f"Error fetching subreddit URLs: {e}")
        return []
    finally:
        connection.close()


def fetch_posts(subreddit_url):
    """
    Fetch posts from a subreddit using Reddit's JSON API.

    Args:
        subreddit_url (str): The base URL of the subreddit.
        max_pages (int): Maximum number of pages to fetch.

    Returns:
        list: A list of post metadata dictionaries.
    """
    posts = []
    after = None

    for page in range(10):
        url = f"{subreddit_url}.json?limit={POSTS_PER_PAGE}"
        if after:
            url += f"&after={after}"

        logging.info(f"Fetching page {page + 1} from {url}")
        try:
            response = requests.get(url, headers={"User-Agent": "PythonScript"})
            response.raise_for_status()
            data = response.json()

            # Extract posts
            children = data.get("data", {}).get("children", [])
            for child in children:
                post = child["data"]
                posts.append(
                    {
                        "post_id": post.get("id"),
                        "subreddit": post.get("subreddit"),
                        "author": post.get("author"),
                        "created_timestamp": post.get("created_utc"),
                        "post_title": post.get("title"),
                        "post_body": post.get("selftext"),
                        "url": post.get("url"),
                        "permalink": urljoin("https://www.reddit.com", post.get("permalink")),
                        "upvotes": post.get("ups"),
                        "score": post.get("score"),
                        "upvote_ratio": post.get("upvote_ratio"),
                        "ups": post.get("ups"),
                        "comments": post.get("num_comments"),
                        "link_flair_text": post.get("link_flair_text"),
                        "thumbnail": post.get("thumbnail"),
                        "thumbnail_width": post.get("thumbnail_width"),
                        "thumbnail_height": post.get("thumbnail_height"),
                        "preview": post.get("preview"),
                        "media_metadata": post.get("media_metadata"),
                        "gallery_data": post.get("gallery_data"),
                        "edited": post.get("edited"),
                        "subreddit_subscribers": post.get("subreddit_subscribers"),
                    }
                )

            # Update 'after' for pagination
            after = data.get("data", {}).get("after")
            if not after:
                logging.info(f"No more pages to fetch for {subreddit_url}")
                break

        except requests.RequestException as e:
            logging.error(f"Error fetching data from {url}: {e}")
            break

    return posts


import json


def save_posts_to_database(posts):
    """
    Save scraped posts to the SQLite database.

    Args:
        posts (list): A list of post metadata dictionaries.
    """
    if not posts:
        logging.warning("No posts to save to the database.")
        return

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    try:
        for post in posts:
            try:
                # Serialize dict fields to JSON strings
                media_metadata = (
                    json.dumps(post.get("media_metadata"))
                    if post.get("media_metadata")
                    else None
                )
                preview = (
                    json.dumps(post.get("preview")) if post.get("preview") else None
                )
                gallery_data = (
                    json.dumps(post.get("gallery_data"))
                    if post.get("gallery_data")
                    else None
                )
                # Convert boolean to integer
                edited = (
                    int(post.get("edited"))
                    if isinstance(post.get("edited"), bool)
                    else post.get("edited")
                )

                cursor.execute(
                    f"""
                    INSERT OR IGNORE INTO {POSTS_TABLE} (
                        post_id,
                        subreddit,
                        author,
                        created_timestamp,
                        post_title,
                        post_body,
                        url,
                        permalink,
                        upvotes,
                        score,
                        upvote_ratio,
                        ups,
                        comments,
                        link_flair_text,
                        thumbnail,
                        thumbnail_width,
                        thumbnail_height,
                        preview,
                        media_metadata,
                        gallery_data,
                        edited,
                        subreddit_subscribers
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        post.get("post_id"),
                        post.get("subreddit"),
                        post.get("author"),
                        post.get("created_timestamp"),
                        post.get("post_title"),
                        post.get("post_body"),
                        post.get("url"),
                        post.get("permalink"),
                        post.get("upvotes"),
                        post.get("score"),
                        post.get("upvote_ratio"),
                        post.get("ups"),
                        post.get("comments"),
                        post.get("link_flair_text"),
                        post.get("thumbnail"),
                        post.get("thumbnail_width"),
                        post.get("thumbnail_height"),
                        preview,  # Serialized JSON string
                        media_metadata,  # Serialized JSON string
                        gallery_data,  # Serialized JSON string
                        edited,  # Convert bool to int
                        post.get("subreddit_subscribers")
                    ),
                )
            except sqlite3.Error as e:
                logging.error(f"SQLite error while inserting post: {e}")
        connection.commit()
        logging.info(f"Successfully saved {len(posts)} posts to the database.")
    finally:
        connection.close()
    """
    Save scraped posts to the SQLite database.

    Args:
        posts (list): A list of post metadata dictionaries.
    """
    if not posts:
        logging.warning("No posts to save to the database.")
        return

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    try:
        for post in posts:
            try:
                # Serialize dict fields to JSON strings
                media_metadata = (
                    json.dumps(post.get("media_metadata"))
                    if post.get("media_metadata")
                    else None
                )
                preview = (
                    json.dumps(post.get("preview")) if post.get("preview") else None
                )
                gallery_data = (
                    json.dumps(post.get("gallery_data"))
                    if post.get("gallery_data")
                    else None
                )

                cursor.execute(
                    f"""
                    INSERT OR IGNORE INTO {POSTS_TABLE} (
                        post_id,
                        subreddit,
                        author,
                        created_timestamp,
                        post_title,
                        post_body,
                        url,
                        permalink,
                        upvotes,
                        score,
                        upvote_ratio,
                        ups,
                        comments,
                        link_flair_text,
                        thumbnail,
                        thumbnail_width,
                        thumbnail_height,
                        preview,
                        media_metadata,
                        gallery_data,
                        edited,
                        subreddit_subscribers
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        post.get("post_id"),
                        post.get("subreddit"),
                        post.get("author"),
                        post.get("created_timestamp"),
                        post.get("post_title"),
                        post.get("post_body"),
                        post.get("url"),
                        post.get("permalink"),
                        post.get("upvotes"),
                        post.get("score"),
                        post.get("upvote_ratio"),
                        post.get("ups"),
                        post.get("comments"),
                        post.get("link_flair_text"),
                        post.get("thumbnail"),
                        post.get("thumbnail_width"),
                        post.get("thumbnail_height"),
                        preview,  # Serialized JSON string
                        media_metadata,  # Serialized JSON string
                        gallery_data,  # Serialized JSON string
                        post.get("edited"),
                        post.get("subreddit_subscribers"),
                    ),
                )
            except sqlite3.Error as e:
                logging.error(f"SQLite error while inserting post: {e}")
        connection.commit()
        logging.info(f"Successfully saved {len(posts)} posts to the database.")
    finally:
        connection.close()

    """
    Save scraped posts to the SQLite database.

    Args:
        posts (list): A list of post metadata dictionaries.
    """
    if not posts:
        logging.warning("No posts to save to the database.")
        return

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    try:
        for post in posts:
            try:
                # Serialize dict fields to JSON strings
                media_metadata = (
                    json.dumps(post.get("media_metadata"))
                    if post.get("media_metadata")
                    else None
                )
                preview = (
                    json.dumps(post.get("preview")) if post.get("preview") else None
                )
                gallery_data = (
                    json.dumps(post.get("gallery_data"))
                    if post.get("gallery_data")
                    else None
                )

                cursor.execute(
                    f"""
                    INSERT OR IGNORE INTO {POSTS_TABLE} (
                        post_id,
                        subreddit,
                        author,
                        created_timestamp,
                        post_title,
                        post_body,
                        url,
                        permalink,
                        upvotes,
                        score,
                        upvote_ratio,
                        ups,
                        comments,
                        link_flair_text,
                        thumbnail,
                        thumbnail_width,
                        thumbnail_height,
                        preview,
                        media_metadata,
                        gallery_data,
                        edited,
                        subreddit_subscribers
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        post.get("post_id"),
                        post.get("subreddit"),
                        post.get("author"),
                        post.get("created_timestamp"),
                        post.get("post_title"),
                        post.get("post_body"),
                        post.get("url"),
                        post.get("permalink"),
                        post.get("upvotes"),
                        post.get("score"),
                        post.get("upvote_ratio"),
                        post.get("ups"),
                        post.get("comments"),
                        post.get("link_flair_text"),
                        post.get("thumbnail"),
                        post.get("thumbnail_width"),
                        post.get("thumbnail_height"),
                        preview,  # Serialized JSON string
                        media_metadata,  # Serialized JSON string
                        gallery_data,  # Serialized JSON string
                        post.get("edited"),
                        post.get("subreddit_subscribers"),
                    ),
                )
            except sqlite3.Error as e:
                logging.error(f"SQLite error while inserting post: {e}")
        connection.commit()
        logging.info(f"Successfully saved {len(posts)} posts to the database.")
    finally:
        connection.close()


def main():
    """
    Main function to scrape Reddit posts and save them to the database.
    """
    logging.info("Starting the Reddit scraper.")

    # Set up the database
    setup_database()

    # Get subreddit URLs
    subreddit_urls = get_subreddit_urls()
    if not subreddit_urls:
        logging.error("No subreddit URLs found in the database.")
        return

    # Scrape posts and save them to the database
    for subreddit_url in subreddit_urls:
        posts = fetch_posts(subreddit_url)
        save_posts_to_database(posts)

    logging.info("Finished scraping Reddit posts.")


if __name__ == "__main__":
    main()
