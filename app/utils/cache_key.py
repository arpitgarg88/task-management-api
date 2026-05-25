"""
Utility helpers for Redis cache key generation.
"""
def task_key(task_id: int) -> str:
    """
    Generates cache key for individual task lookup.
    """
    return f"task:{task_id}"


def tasks_user_key(user_id: int) -> str:
    """
    Generates cache key for user task listings.
    """
    return f"tasks:user:{user_id}"