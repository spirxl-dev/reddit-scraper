import asyncio
import sqlite3
import time
from asyncpraw import Reddit


async def fetch_comments(praw_client, post_id):
    """
    Fetch all comments for a given Reddit post ID using Async PRAW.
    Args:
        praw_client (asyncpraw.Reddit): The Async PRAW client instance.
        post_id (str): The Reddit post ID.
    Returns:
        list: A list of comment dictionaries with post_id, body, and author.
    """
    try:
        submission = await praw_client.submission(id=post_id)
        await submission.comments.replace_more(limit=10)
        all_comments = submission.comments.list()

        comments_data = [
            {
                "post_id": post_id,
                "body": comment.body,
                "author": str(comment.author) if comment.author else "[deleted]",
            }
            for comment in all_comments
        ]

        print(f"Fetched {len(comments_data)} comments for post ID {post_id}.")
        time.sleep(0.25)
        return comments_data

    except Exception as e:
        print(f"Error fetching comments for post ID {post_id}: {e}")
        return []


async def main():
    """
    Main function to fetch comments for all post IDs in the database and print them to the terminal.
    """

    praw = Reddit(
        client_id="XYr7CNOBXmFf0YS3GcHxQA",
        client_secret="p-FaLlz5zK-QKmPoRHxhUtO7UbqPFQ",
        user_agent="MyRedditBot/1.0 by YourUsername",
    )

    database_path = "database/data.db"
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='comments'"
        )
        if not cursor.fetchone():
            print("The `comments` table does not exist in the database.")
            return

        cursor.execute("SELECT DISTINCT post_id FROM comments;")
        post_ids = [row[0] for row in cursor.fetchall()]
        print(f"Found {len(post_ids)} post IDs to process.")

        for post_id in post_ids:
            comments = await fetch_comments(praw, post_id)
            for comment in comments:
                cursor.execute(
                    """
                    INSERT INTO comments (post_id, body, author)
                    VALUES (?, ?, ?)
                    """,
                    (comment["post_id"], comment["body"], comment["author"]),
                )
                connection.commit()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        connection.close()


if __name__ == "__main__":
    asyncio.run(main())
