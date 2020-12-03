import pandas, os, json
from django.conf import settings
from django.db import connection
from celery import shared_task
from upload_app.helpers import create_table, process_row, upload_successful
from shared.helpers import redis_instance, update_task_progress

@shared_task
def start_upload_task(task_name: str):
    create_table(task_name)

    df = pandas.read_csv(os.path.join(settings.BASE_DIR, 'sample_data.csv'))
    rows = [list(row) for row in df.values]
    current_row_index = 0
    
    task_status = {'status': 'run'}
    if not redis_instance.get(task_name):
        redis_instance.set(task_name, json.dumps(task_status))
    else:
        task_status = json.loads(redis_instance.get(task_name))


    while task_status.get('status') == 'run' and current_row_index < len(rows):
        row = rows[current_row_index]
        process_row(task_name, row, current_row_index)
        current_row_index += 1
        update_task_progress(task_name, current_row_index, len(rows))
        task_status = json.loads(redis_instance.get(task_name))
    
    if task_status.get('status') == 'pause':
        task_status = json.loads(redis_instance.get(task_name))
        task_status['current_row_index'] = current_row_index
        redis_instance.set(task_name, json.dumps(task_status))
        return
    
    # Upload finished successfully
    upload_successful(task_name)
    

@shared_task
def resume_upload_task(task_name: str):
    task_status = json.loads(redis_instance.get(task_name))
    
    df = pandas.read_csv(os.path.join(settings.BASE_DIR, 'sample_data.csv'))
    rows = [list(row) for row in df.values]
    current_row_index = task_status.get('current_row_index')

    while task_status.get("status") == "run" and current_row_index < len(rows):
        row = rows[current_row_index]
        process_row(task_name, row, current_row_index)
        current_row_index += 1
        update_task_progress(task_name, current_row_index, len(rows))
        task_status = json.loads(redis_instance.get(task_name))
    
    if task_status.get("status") == "pause":
        task_status = json.loads(redis_instance.get(task_name))
        task_status['current_row_index'] = current_row_index
        redis_instance.set(task_name, json.dumps(task_status))
        return
    
    # Upload finished successfully
    upload_successful(task_name)

@shared_task
def rollback_upload_task(task_name: str):
    UploadStatus.objects.filter(table_name=task_name).delete()
    
    # delete task associated data from redis
    redis_instance.delete(task_name)
    redis_instance.delete(f"{task_name}__progress")
    
    # Drop table
    with connection.cursor() as c:
        query = f"DROP TABLE IF EXISTS {task_name}"
        c.execute(query)