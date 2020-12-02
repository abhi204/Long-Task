from django.db import models

# Create your models here.
class UploadStatus(models.Model):
    user_id = models.TextField()
    table_name = models.TextField()
    task_completed = models.BooleanField(default=False)
