import csv
import random
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker for realistic text generation
fake = Faker()

# Constants
NUM_USERS = 4500  # 4.5k users
NUM_POSTS = 10000  # 10k posts
NUM_INTERESTS = 20  # 20 unique interests
NUM_LIKES = 80000  # 80k likes
NUM_COMMENTS = 50000  # 50k comments
NUM_COMMENT_REPLIES = 30000  # 30k comment replies
NUM_SAVED_POSTS = 20000  # 20k saved posts

# Generate random interests
interests = [
    "Politics", "Music", "Technology", "Sports", "Travel", "Food", "Fashion", 
    "Health", "Movies", "Gaming", "Art", "Science", "Business", "Education", 
    "Environment", "Fitness", "Photography", "Literature", "History", "Cooking"
]

# Generate users
users = [i for i in range(1, NUM_USERS + 1)]

# Generate users_has_interests
users_has_interests = []
for user_id in users:
    user_interests = random.sample(interests, k=random.randint(1, 3))  # Each user has 1-3 interests
    for interest in user_interests:
        users_has_interests.append([len(users_has_interests) + 1, user_id, interest, datetime.now(), datetime.now()])

# Write users_has_interests to CSV
with open("users_has_interests.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["id", "user_id", "interest", "created_at", "modified_at"])
    writer.writerows(users_has_interests)

# Helper function to get user interests
def get_user_interests(user_id):
    return [row[2] for row in users_has_interests if row[1] == user_id]

# Generate posts
posts = []
for post_id in range(1, NUM_POSTS + 1):
    user_id = random.choice(users)
    user_type = random.choice(["user", "page"])
    user_interests = get_user_interests(user_id)
    description = f"{fake.sentence()}. This post is about {random.choice(user_interests)}."
    has_files = random.choice([0, 1])
    no_of_likes = random.randint(0, 1000)
    no_of_comments = random.randint(0, 500)
    no_of_shares = random.randint(0, 200)
    no_of_saves = random.randint(0, 300)
    post_privacy = random.choice([0, 1])
    created_at = datetime.now() - timedelta(days=random.randint(0, 30))
    modified_at = created_at + timedelta(minutes=random.randint(0, 60))
    posts.append([post_id, user_id, user_type, description, has_files, no_of_likes, no_of_comments, no_of_shares, no_of_saves, post_privacy, created_at, modified_at])

# Write posts to CSV
with open("posts.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["id", "user_id", "user_type", "description", "has_files", "no_of_likes", "no_of_comments", "no_of_shares", "no_of_saves", "post_privacy", "created_at", "modified_at"])
    writer.writerows(posts)

# Generate posts_has_likes
posts_has_likes = []
for like_id in range(1, NUM_LIKES + 1):
    post_id = random.choice(posts)[0]
    liked_by = random.choice(users)
    posts_has_likes.append([like_id, post_id, liked_by, None, datetime.now(), datetime.now()])

# Write posts_has_likes to CSV
with open("posts_has_likes.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["id", "posts_id", "liked_by", "notification_id", "created_at", "modified_at"])
    writer.writerows(posts_has_likes)

# Generate posts_has_comments
posts_has_comments = []
for comment_id in range(1, NUM_COMMENTS + 1):
    post_id = random.choice(posts)[0]
    commented_by = random.choice(users)
    user_interests = get_user_interests(commented_by)
    comment = f"{fake.sentence()}. This comment is about {random.choice(user_interests)}."
    no_of_likes = random.randint(0, 100)
    no_of_comment_replies = random.randint(0, 50)
    posts_has_comments.append([comment_id, post_id, commented_by, comment, no_of_likes, no_of_comment_replies, None, datetime.now(), datetime.now()])

# Write posts_has_comments to CSV
with open("posts_has_comments.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["id", "posts_id", "commented_by", "comment", "no_of_likes", "no_of_comment_replies", "notification_id", "created_at", "modified_at"])
    writer.writerows(posts_has_comments)

# Generate post_comments_has_comments
post_comments_has_comments = []
for reply_id in range(1, NUM_COMMENT_REPLIES + 1):
    post_has_comments_id = random.choice(posts_has_comments)[0]
    commented_by = random.choice(users)
    user_interests = get_user_interests(commented_by)
    comment = f"{fake.sentence()}. This reply is about {random.choice(user_interests)}."
    no_of_likes = random.randint(0, 50)
    post_comments_has_comments.append([reply_id, post_has_comments_id, commented_by, comment, None, no_of_likes, datetime.now(), datetime.now()])

# Write post_comments_has_comments to CSV
with open("post_comments_has_comments.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["id", "post_has_comments_id", "commented_by", "comment", "notification_id", "no_of_likes", "created_at", "modified_at"])
    writer.writerows(post_comments_has_comments)

# Generate saved_posts
saved_posts = []
for save_id in range(1, NUM_SAVED_POSTS + 1):
    user_id = random.choice(users)
    post_id = random.choice(posts)[0]
    saved_posts.append([save_id, user_id, post_id, datetime.now(), datetime.now()])

# Write saved_posts to CSV
with open("saved_posts.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["id", "user_id", "posts_id", "created_at", "modified_at"])
    writer.writerows(saved_posts)