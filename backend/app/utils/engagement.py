def compute_engagement_rate(likes: int, comments: int, views: int) -> float:
    """
    engagement_rate = ((likes + comments) / views) * 100
    Returns 0.0 if views is 0 to avoid ZeroDivisionError.
    """
    if views == 0:
        return 0.0
    return round(((likes + comments) / views) * 100, 4)