import os, csv
from django.conf import settings
from django.db import connection
from download_app.models import DownloadStatus
from shared.helpers import redis_instance

def count_rows(table_name):
    with connection.cursor() as c:
        query = f'select count(*) from {table_name}'
        c.execute(query)
        return c.fetchone()[0]

def process_csv(filename, table_name, row_sid):
    '''
    Adds a row from table to csv file
    '''
    row = []
    with connection.cursor() as c:
        query = f'SELECT * FROM {table_name} WHERE "Sid"={row_sid}'
        c.execute(query)
        row = list(c.fetchone())
    
    with open(os.path.join(settings.BASE_DIR, 'static', f"{filename}.csv"), "a+") as csv_file:
        csvwriter = csv.writer(csv_file)
        csvwriter.writerow(row)

def download_successful(table_name):
    # Allow user to perform next download
    download_details = DownloadStatus.objects.get(table_name=table_name)
    download_details.task_completed = True
    download_details.save()

    # delete associated data from redis
    redis_instance.delete(table_name)