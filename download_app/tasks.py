import csv, os, json
from django.conf import settings
from celery import shared_task
from download_app.helpers import count_rows, process_csv, download_successful
from download_app.models import DownloadStatus
from shared.helpers import redis_instance

@shared_task(name='start_download')
def start_download_task(task_name: str, filename: str):

    with open(os.path.join(settings.BASE_DIR, 'static', f"{filename}.csv"), "a+") as csv_file:
        csvwriter = csv.writer(csv_file)
        csvwriter.writerow([
            'Sid',
            'Region',
            'Country',
            'Item Type',
            'Sales Channel',
            'Order Priority',
            'Order ID',
            'Units Sold',
            'Unit Price',
            'Unit Cost',
            'Total Revenue',
            'Total Cost',
            'Total Profit']
        )

    row_count = count_rows(task_name)
    current_row = 0
    
    task_status = {'status': 'run'}
    if not redis_instance.get(task_name):
        redis_instance.set(task_name, json.dumps(task_status))
    else:
        task_status = json.loads(redis_instance.get(task_name))


    while task_status.get('status') == 'run' and current_row < row_count:
        process_csv(filename, task_name, current_row)
        current_row += 1
        progress = current_row/row_count
        redis_instance.set(f"{task_name}__progress", progress)
        task_status = json.loads(redis_instance.get(task_name))
    
    if task_status.get('status') == 'pause':
        task_status = json.loads(redis_instance.get(task_name))
        task_status['current_row'] = current_row
        redis_instance.set(task_name, json.dumps(task_status))
        return
    
    # download finished successfully
    download_successful(task_name)
    

@shared_task(name="resume_download")
def resume_download_task(task_name: str):
    task_status = json.loads(redis_instance.get(task_name))
    row_count = count_rows(task_name)
    current_row = task_status.get('current_row')

    while task_status.get('status') == 'run' and current_row < row_count:
        process_csv(filename, task_name, current_row)
        current_row += 1
        task_status = json.loads(redis_instance.get(task_name))
    
    if task_status.get('status') == 'pause':
        task_status = json.loads(redis_instance.get(task_name))
        task_status['current_row'] = current_row
        redis_instance.set(task_name, json.dumps(task_status))
        return
    
    # download finished successfully
    download_successful(task_name)

@shared_task(name="rollback_download")
def rollback_download_task(task_name: str):
    filename = DownloadStatus.objects.get(table_name=task_name).filename
    DownloadStatus.objects.filter(table_name=task_name).delete()
    
    # delete task associated data from redis
    redis_instance.delete(task_name)
    redis_instance.delete(f"{task_name}__progress")
    
    # Delete CSV file
    os.remove(os.path.join(settings.BASE_DIR, 'static', f"{filename}.csv"))