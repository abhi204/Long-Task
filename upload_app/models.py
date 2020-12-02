from django.db import models

# Create your models here.
class ProcessedData(models.Model):
    task_id = models.TextField()
    region = models.TextField()
    country = models.CharField(max_length=200)
    item_type = models.CharField(max_length=200)
    sales_channel = models.CharField(max_length=200)
    order_priority = models.CharField(max_length=1)
    order_date = models.DateField()
    order_id = models.BigIntegerField()
    ship_date = models.DateField()
    units_sold = models.BigIntegerField()
    unit_price = models.FloatField()
    unit_cost = models.FloatField()
    total_revenue = models.FloatField()
    total_cost = models.FloatField()
    total_profit = models.FloatField()
