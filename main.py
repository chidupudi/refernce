import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
import json

def find_column(df, possible_names):
    """Helper function to find columns with similar names"""
    for name in possible_names:
        matches = [col for col in df.columns if name.lower() in col.lower()]
        if matches:
            return matches[0]
    return None

def get_or_assign_interests(user_id, users_has_interests):
    """Get or assign top 3 interests for a user"""
    user_id_col = find_column(users_has_interests, ["user_id"])
    interest_col = find_column(users_has_interests, ["interest"])
    
    if not user_id_col or not interest_col:
        return []
    
    user_interests = users_has_interests[users_has_interests[user_id_col] == user_id][interest_col].tolist()
    
    # Handle cases where user has 0-2 interests
    if not user_interests:
        top_interests = users_has_interests[interest_col].value_counts().head(3).index.tolist()
        user_interests = top_interests
    elif len(user_interests) == 1:
        top_interests = users_has_interests[interest_col].value_counts().index.tolist()
        interests_to_add = [i for i in top_interests if i not in user_interests][:2]
        user_interests.extend(interests_to_add)
    elif len(user_interests) == 2:
        top_interests = users_has_interests[interest_col].value_counts().index.tolist()
        interest_to_add = next((i for i in top_interests if i not in user_interests), None)
        if interest_to_add:
            user_interests.append(interest_to_add)
    
    return [i.strip() for i in user_interests[:3]]  # Clean whitespace

def update_interests(user_interests, recent_activity, posts):
    """Update user interests based on recent activity"""
    if not recent_activity or not user_interests:
        return user_interests
    
    post_id_col = find_column(posts, ["id", "post_id"]) or posts.columns[0]
    desc_col = find_column(posts, ["desc", "description", "content"])
    
    if not desc_col:
        return user_interests
    
    activity_posts = posts[posts[post_id_col].isin(recent_activity)]
    if activity_posts.empty:
        return user_interests
    
    matches = []
    for desc in activity_posts[desc_col].dropna():
        for interest in user_interests:
            if re.search(interest, str(desc), re.IGNORECASE):
                matches.append(interest)
    
    if not matches:
        return user_interests
    
    from collections import Counter
    interest_counts = Counter(matches)
    sorted_interests = [interest for interest, _ in interest_counts.most_common()]
    
    if sorted_interests:
        if len(user_interests) == 1:
            user_interests[-1] = sorted_interests[0]
        else:
            user_interests[-1] = sorted_interests[0]
    
    return user_interests

def generate_recommendations(user_id):
    """Main function to generate recommendations for a user"""
    # Load data
    posts = pd.read_csv("posts.csv")
    users_has_interests = pd.read_csv("users_has_interests.csv")
    posts_has_likes = pd.read_csv("posts_has_likes.csv")
    posts_has_comments = pd.read_csv("posts_has_comments.csv")
    saved_posts = pd.read_csv("saved_posts.csv")
    
    # Get user interests
    top_3_interests = get_or_assign_interests(user_id, users_has_interests)
    
    # Get recent activity
    likes_user_col = find_column(posts_has_likes, ["user", "liked_by"])
    likes_post_col = find_column(posts_has_likes, ["post", "posts_id"])
    likes_date_col = find_column(posts_has_likes, ["date", "created"])
    
    recent_likes = []
    if likes_user_col and likes_post_col and likes_date_col:
        recent_likes = posts_has_likes[
            (posts_has_likes[likes_user_col] == user_id) & 
            (pd.to_datetime(posts_has_likes[likes_date_col]) >= datetime.now() - timedelta(days=30))
        ][likes_post_col].tolist()
    
    recent_activity = list(set(recent_likes))
    
    # Update interests based on activity
    user_interests = update_interests(top_3_interests, recent_activity, posts)
    
    # Filter posts relevant to interests
    desc_col = find_column(posts, ["desc", "description", "content"]) or posts.columns[0]
    relevant_posts = posts.copy()
    
    if desc_col and user_interests:
        mask = relevant_posts[desc_col].astype(str).str.contains('|'.join(user_interests), case=False, na=False)
        relevant_posts = relevant_posts[mask].copy()
    
    # Score posts based on engagement
    likes_col = find_column(posts, ["likes", "no_of_likes"])
    comments_col = find_column(posts, ["comments", "no_of_comments"])
    shares_col = find_column(posts, ["shares", "no_of_shares"])
    date_col = find_column(posts, ["date", "created_at"])
    
    if likes_col and comments_col and shares_col and date_col:
        relevant_posts["engagement_score"] = (
            relevant_posts[likes_col] / 1000 + 
            relevant_posts[comments_col] / 500 + 
            relevant_posts[shares_col] / 200
        )
        relevant_posts["recency_score"] = relevant_posts[date_col].apply(
            lambda x: 1 if pd.to_datetime(x) >= datetime.now() - timedelta(days=7) else 0.5
        )
        relevant_posts["total_score"] = 0.7 * relevant_posts["engagement_score"] + 0.3 * relevant_posts["recency_score"]
    else:
        relevant_posts["total_score"] = 1.0
    
    # Get top interest-based posts
    post_id_col = find_column(posts, ["id", "post_id"]) or posts.columns[0]
    top_interest_posts = relevant_posts.sort_values("total_score", ascending=False).head(50)
    
    # Get viral posts (top 50 by engagement)
    viral_posts = posts.copy()
    if date_col and likes_col:
        viral_posts = posts[
            (pd.to_datetime(posts[date_col]) >= datetime.now() - timedelta(days=7))
        ].sort_values(likes_col, ascending=False).head(50)
    else:
        viral_posts = posts.head(50)
    
    # Combine recommendations
    if not relevant_posts.empty:
        top_interest_posts["final_score"] = top_interest_posts["total_score"] * 1.5
        viral_posts["final_score"] = viral_posts[likes_col] if likes_col in viral_posts else 1.0
        final_recommendations = pd.concat([top_interest_posts, viral_posts]).drop_duplicates(subset=[post_id_col])
        final_recommendations = final_recommendations.sort_values("final_score", ascending=False).head(100)
    else:
        final_recommendations = viral_posts.head(50)
    
    # Prepare JSON output
    recommendations = []
    for _, post in final_recommendations.iterrows():
        post_id = post[post_id_col]
        description = post[desc_col] if desc_col in post else "No description available"
        likes = post[likes_col] if likes_col in post else 0
        comments = post[comments_col] if comments_col in post else 0
        shares = post[shares_col] if shares_col in post else 0
        created_at = post[date_col] if date_col in post else "Unknown date"
        
        # Check if post matches interests
        matches_interests = False
        matching_interests = []
        if desc_col and user_interests:
            for interest in user_interests:
                if isinstance(description, str) and interest.lower() in description.lower():
                    matches_interests = True
                    matching_interests.append(interest)
        
        if matches_interests:
            reason = f"Matches your interests in {', '.join(matching_interests)}"
        else:
            reason = "Popular post with high engagement"
        
        recommendations.append({
            "post_id": int(post_id),
            "description": str(description),
            "likes": int(likes),
            "comments": int(comments),
            "shares": int(shares),
            "created_at": str(created_at),
            "reason": reason,
            "matches_interests": matches_interests
        })
    
    return {
        "user_id": user_id,
        "interests": user_interests,
        "recommendations": recommendations,
        "count": len(recommendations)
    }

# Example usage
if __name__ == "__main__":
    user_id = 4  # Change this to the desired user ID
    recommendations = generate_recommendations(user_id)
    print(json.dumps(recommendations, indent=2))