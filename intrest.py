import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Parameters
num_users = 8500  # Total number of users
num_interests = 15  # Number of unique interests
min_interests_per_user = 0  # Minimum interests per user (0 for some users with no interests)
max_interests_per_user = 3  # Maximum interests per user
start_date = datetime(2023, 1, 1)  # Start date for timestamps
end_date = datetime(2025, 3, 5)  # End date for timestamps

# Predefined list of interests
interests_list = [
    "Gaming", "Politics", "Environment", "Business", "Cooking", "Travel", "Literature",
    "Photography", "Technology", "Fitness", "Music", "Art", "Science", "Sports", "Fashion"
]

# Generate synthetic data
data = []
user_id = 1
while len(data) < num_users:
    # Randomly decide the number of interests for this user (0 to 3)
    num_user_interests = np.random.randint(min_interests_per_user, max_interests_per_user + 1)
    
    # Assign interests to the user
    for _ in range(num_user_interests):
        interest = np.random.choice(interests_list)  # Randomly select an interest
        created_at = start_date + timedelta(days=np.random.randint(0, (end_date - start_date).days))
        modified_at = created_at + timedelta(days=np.random.randint(0, 30))  # Modified within 30 days
        data.append({
            "id": len(data) + 1,
            "user_id": user_id,
            "interest": interest,
            "created_at": created_at,
            "modified_at": modified_at
        })
    
    user_id += 1

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("users_has_interests.csv", index=False)

print("Dataset generated and saved to 'users_has_interests.csv'.")
print(df.head())