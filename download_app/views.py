import csv, uuid, json,os
from django.conf import settings
from .models import DownloadStatus
from upload_app.models import UploadStatus
from .tasks import start_download_task, resume_download_task, rollback_download_task
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from shared.helpers import redis_instance


# Create your views here.
class StartDownloadView(APIView):

    def post(self, request, format=None):
        '''
        Starts download task and returns task name
        '''
        try:
            user_id = request.data.get('user_id')
            task_name = request.data.get('task_name')

            # Check if any previous download task is being executed
            if DownloadStatus.objects.filter(user_id=user_id, task_completed=False).exists():
                return Response({"message": "A previous download task is being executed. Please wait for it to finish"}, status=status.HTTP_403_FORBIDDEN)
            # Check if requested table exists
            elif not UploadStatus.objects.filter(user_id=user_id, task_completed=True, table_name=task_name).exists():
                return Response({"message": "Upload pending or invalid task_name"}, status=status.HTTP_403_FORBIDDEN)
            # TODO: If already generated CSV: Directly give download link
            elif DownloadStatus.objects.filter(user_id=user_id, table_name=task_name, task_completed=True).exists():
                return Response({"download_url": f"http://localhost:8000/static/{DownloadStatus.objects.filter(user_id=user_id, table_name=task_name, task_completed=True).filename}.csv"})
            
            filename = str(uuid.uuid4())
            DownloadStatus.objects.create(
                user_id=user_id,
                table_name=task_name,
                task_completed=False,
                filename=filename
            )
            
            # start upload task using celery worker
            start_download_task.delay(task_name, filename)

            return Response({
                "task_name": task_name
            })

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class PauseDownloadView(APIView):

    def post(self, request, format=None):
        '''
        Pause ongoing download task
        '''

        try:
            task_name = request.data.get('task_name')
            
            # set task status to paused
            task_status = json.loads(redis_instance.get(task_name))
            task_status['status'] = 'pause'
            redis_instance.set(task_name, json.dumps(task_status))

            return Response({
                "task_name": task_name
            })

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ResumeDownloadView(APIView):

    def post(self, request, format=None):
        '''
        Resume a paused Download task
        '''

        try:
            task_name = request.data.get('task_name')
        
            # Set task status to run
            task_status = json.loads(redis_instance.get(task_name))
            task_status['status'] = 'run'
            redis_instance.set(task_name, json.dumps(task_status))

            # Run the background process for resuming the task
            resume_download_task.delay(task_name)

            return Response({
                "task_name": task_name
            })

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class TerminateDownloadView(APIView):

    def post(self, request, format=None):
        '''
        Terminate an ongoing download task
        '''
        try:
            task_name = request.data.get('task_name')

            # Set task status to terminate
            task_status = json.loads(redis_instance.get(task_name))
            task_status['status'] = 'terminate'
            redis_instance.set(task_name, json.dumps(task_status))

            # Run the background process for rolling back the changes
            rollback_download_task.delay(task_name)

            return Response({
                "task_name": task_name
            })
        
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class DownloadProgressView(APIView):
    def post(self, request, format=None):
        '''
        Get download progress. Returns download url if csv generated successfully
        '''
        try:
            user_id = request.data.get('user_id')
            task_name = request.data.get('task_name')

            # Check if requested table exists
            if not UploadStatus.objects.filter(user_id=user_id, task_completed=True, table_name=task_name).exists():
                return Response({"message": "Upload pending or invalid task_name"}, status=status.HTTP_403_FORBIDDEN)
            # TODO: If already generated CSV: Directly give download link
            elif DownloadStatus.objects.filter(user_id=user_id, table_name=task_name, task_completed=True).exists():
                return Response({"download_url": f"http://localhost:8000/static/{DownloadStatus.objects.get(user_id=user_id, table_name=task_name, task_completed=True).filename}.csv"})
            
            return Response({
                "progress": redis_instance.get(f"{task_name}__progress")
            })

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)