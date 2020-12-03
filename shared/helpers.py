import redis
from django.conf import settings

redis_instance = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT, 
    db=0
)

def update_task_progress(task_name, current_row, total_rows):
    progress = (current_row/total_rows) * 100
    redis_instance.set(f"{task_name}__progress", f"{int(progress)} %")