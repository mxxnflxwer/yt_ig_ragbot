from app.services.youtube_service import get_youtube_data

url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
data = get_youtube_data(url)

print(f"Title     : {data['title']}")
print(f"Creator   : {data['creator_name']}")
print(f"Followers : {data['follower_count']}")
print(f"Views     : {data['views']}")
print(f"Likes     : {data['likes']}")
print(f"Comments  : {data['comments']}")
print(f"Duration  : {data['duration_seconds']}s")
print(f"Hashtags  : {data['hashtags']}")
print(f"Transcript: {data['transcript'][:200]}")