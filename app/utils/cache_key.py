def task_key(task_id: int) -> str:
    return f"task:{task_id}"


def tasks_user_key(user_id: int) -> str:
    return f"tasks:user:{user_id}"