from app.services.embedding_service import chunk_and_embed
from app.services.rag_service import ask

session_id = "test_rag_001"

# Embed test transcripts
transcript_a = """
Welcome to this video about content creation. Today we are going to talk about 
how to grow your audience on social media. The most important thing is consistency.
Post every day, engage with your audience, and always respond to comments.
The hook in the first five seconds is critical. You need to grab attention immediately.
Use trending audio, keep videos under 60 seconds, and always add captions.
"""

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

chunk_and_embed(session_id, "A", transcript_a, metadata_a)
chunk_and_embed(session_id, "B", transcript_b, metadata_b)

# Test questions
questions = [
    "What is the engagement rate of each video?",
    "Compare the hooks in the first 5 seconds",
    "Why did Video B get more engagement than Video A?",
]

for q in questions:
    print(f"\nQ: {q}")
    result = ask(session_id, q)
    print(f"A: {result['answer']}")
    print(f"Sources: {[s['video_id'] for s in result['sources']]}")
    print("-" * 60)