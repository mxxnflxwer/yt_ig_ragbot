from app.services.instagram_service import get_instagram_data

url = "https://www.instagram.com/reel/DXLb7Yak35n/?igsh=bzVndndydWJqajZk"
data = get_instagram_data(url)

print(f"Title     : {data['title']}")
print(f"Creator   : {data['creator_name']}")
print(f"Followers : {data['follower_count']}")
print(f"Views     : {data['views']}")
print(f"Likes     : {data['likes']}")
print(f"Comments  : {data['comments']}")
print(f"Duration  : {data['duration_seconds']}s")
print(f"Hashtags  : {data['hashtags']}")
print(f"Engagement: {data['engagement_rate']}%")
print(f"Transcript: {data['transcript'][:200]}")