import pandas, os, json
from django.conf import settings
from celery import shared_task
from upload_app.helpers import process_row
from upload_app.models import ProcessedData
from shared.helpers import redis_instance

@shared_task(name="start_upload")
def start_upload_task(task_id: str):
    df = pandas.read_csv(os.path.join(settings.BASE_DIR, 'sample_data.csv'))
    rows = [list(row) for row in df.values]
    current_row_index = 0
    
    task_status = {"status": "run"}
    if not redis_instance.get(task_id):
        redis_instance.set(task_id, json.dumps(task_status))
    else:
        task_status = json.loads(redis_instance.get(task_id))

    while task_status.get("status") == "run" and current_row_index < len(rows):
        row = rows[current_row_index]
        process_row(task_id, row)
        current_row_index += 1
        task_status = json.loads(redis_instance.get(task_id))
    
    if task_status.get("status") == "pause":
        task_status = json.loads(redis_instance.get(task_id))
        task_status['current_row_index'] = current_row_index
        redis_instance.set(task_id, json.dumps(task_status))

@shared_task(name="resume_upload")
def resume_upload_task(task_id: str):
    task_status = json.loads(redis_instance.get(task_id))
    
    df = pandas.read_csv(os.path.join(settings.BASE_DIR, 'sample_data.csv'))
    rows = [list(row) for row in df.values]
    current_row_index = task_status.get('current_row_index')

    while task_status.get("status") == "run" and current_row_index < len(rows):
        row = rows[current_row_index]
        process_row(task_id, row)
        current_row_index += 1
        task_status = json.loads(redis_instance.get(task_id))
    
    if task_status.get("status") == "pause":
        task_status = json.loads(redis_instance.get(task_id))
        task_status['current_row_index'] = current_row_index
        redis_instance.set(task_id, json.dumps(task_status))

@shared_task(name="rollback_upload")
def rollback_upload_task(task_id: str):

    # delete task assosiated data from redis
    redis_instance.delete(task_id)
    
    # Delete rows from DB (Rollback changes)
    ProcessedData.objects.filter(task_id=task_id).delete()