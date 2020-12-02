import datetime
from upload_app.models import ProcessedData

def process_row(task_id: str, csv_row: list):
    '''
    processes the incoming data from csv file and saves it to the database
    '''

    format_str = '%m/%d/%Y' # The date format in csv_row

    data = dict(
        task_id=task_id,
        region = csv_row[0],
        country=csv_row[1],
        item_type=csv_row[2],
        sales_channel=csv_row[3],
        order_priority=csv_row[4],
        order_date=datetime.datetime.strptime(csv_row[5], format_str).date(),
        order_id=csv_row[6],
        ship_date=datetime.datetime.strptime(csv_row[7], format_str).date(),
        units_sold=csv_row[8],
        unit_price=csv_row[9],
        unit_cost=csv_row[10],
    )

    # Process csv data to determine total cost,revenue & profit for the current csv file row
    data['total_revenue'] = data['units_sold'] * data['unit_price'] 
    data['total_cost'] = data['units_sold'] * data['unit_cost']
    data['total_profit'] = data['total_revenue'] - data['total_cost']

    ProcessedData.objects.create(**data)