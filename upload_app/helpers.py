from django.db import connection
from shared.helpers import redis_instance
from upload_app.models import UploadStatus

def create_table(table_name):
    '''
    Method to create a table for storing the processed data from CSV.
    '''
    with connection.cursor() as c:
        query = f'CREATE TABLE {table_name} (\
        Sid SERIAL PRIMARY KEY, \
        Region varchar(255), \
        Country varchar(255), \
        "Item Type" varchar(255), \
        "Sales Channel" varchar(255), \
        "Order Priority" varchar(255), \
        "Order ID" varchar(255), \
        "Units Sold" FLOAT,\
        "Unit Price" FLOAT,\
        "Unit Cost" FLOAT,\
        "Total Revenue" FLOAT,\
        "Total Cost" FLOAT,\
        "Total Profit" FLOAT\
        );'
        c.execute(query)

def process_row(table_name: str, row_data: list):
    '''
    processes the incoming data from csv file and saves it to the database
    '''

    row_string = ""
    for data in row_data:
        # Escape string characters before saving in database
        if type(data) is str:
            data = data.replace("'", "''")
            data = data.replace('"', '""')
        row_string += f"'{data}',"
    row_string = row_string[:-1] # remove trailing ","

    with connection.cursor() as c:
        query = f'''INSERT INTO {table_name} (\
        `Region`,\
        `Country`,\
        `Item Type`,\
        `Sales Channel`,\
        `Order Priority`,\
        `Order ID`,\
        `Units Sold`,\
        `Unit Price`,\
        `Unit Cost`,\
        `Total Revenue`,\
        `Total Cost`,\
        `Total Profit`\
        )\
        VALUES ({row_string})'''
        c.execute(query)

def upload_successful(table_name):
    # Allow user to perform next upload
    upload_details = UploadStatus.objects.get(table_name=table_name)
    upload_details.task_completed = True
    upload_details.save()

    # delete associated data from redis
    redis_instance.delete(table_name)