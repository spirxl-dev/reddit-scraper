import praw
import json

# Authenticate with Reddit
reddit = praw.Reddit(
    client_id="XYr7CNOBXmFf0YS3GcHxQA",
    client_secret="p-FaLlz5zK-QKmPoRHxhUtO7UbqPFQ",
    user_agent="MyRedditBot/0.1 by YourUsername",
)

# Replace with the Reddit post ID
post_id = "1gtri6k"  # Example post ID from the provided file
submission = reddit.submission(id=post_id)


# Fetch all comments
submission.comments.replace_more(limit=None)  # Expand "more comments"
all_comments = submission.comments.list()


comments_data = [
    {"id": comment.id, "body": comment.body, "author": str(comment.author)}
    for comment in all_comments
]
with open("comments.json", "w") as file:
    json.dump(comments_data, file, indent=4)
