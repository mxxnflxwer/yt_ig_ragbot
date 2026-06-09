from app.services.embedding_service import chunk_and_embed, get_vectorstore

session_id = "test_session_001"

# Simulate video A transcript
transcript_a = """
Welcome to this video about content creation. Today we are going to talk about 
how to grow your audience on social media. The most important thing is consistency.
Post every day, engage with your audience, and always respond to comments.
The hook in the first five seconds is critical. You need to grab attention immediately.
Use trending audio, keep videos under 60 seconds, and always add captions.
"""

# Simulate video B transcript  
transcript_b = """
Hey guys, today I want to share my journey of growing from zero to one million followers.
It took me two years of daily posting. The key was finding my niche early.
I focused on cooking content and built a loyal community.
Engagement rate matters more than follower count. 
Always ask questions in your captions to drive comments.
"""

metadata_a = {
    "platform": "youtube", "title": "Content Creation Tips",
    "creator_name": "Creator A", "views": 100000,
    "likes": 5000, "comments": 300, "engagement_rate": 5.3,
    "upload_date": "2024-01-01", "duration_seconds": 120, "url": "https://youtube.com/test"
}

metadata_b = {
    "platform": "instagram", "title": "My Growth Journey",
    "creator_name": "Creator B", "views": 50000,
    "likes": 8000, "comments": 500, "engagement_rate": 17.0,
    "upload_date": "2024-02-01", "duration_seconds": 60, "url": "https://instagram.com/test"
}

chunks_a = chunk_and_embed(session_id, "A", transcript_a, metadata_a)
chunks_b = chunk_and_embed(session_id, "B", transcript_b, metadata_b)

print(f"\nVideo A chunks: {chunks_a}")
print(f"Video B chunks: {chunks_b}")

# Test retrieval
vectorstore = get_vectorstore(session_id)
results = vectorstore.similarity_search("what is the hook strategy?", k=3)
print(f"\nTop 3 results for 'hook strategy':")
for r in results:
    print(f"  [{r.metadata['video_id']}] {r.page_content[:100]}")