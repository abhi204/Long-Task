import uuid, json
from .models import UploadStatus
from .tasks import start_upload_task, resume_upload_task, rollback_upload_task
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from shared.helpers import redis_instance


# Create your views here.
class StartUploadView(APIView):

    def post(self, request, format=None):
        '''
        Starts upload task and returns task id
        '''
        try:
            user_id = request.data.get('user_id')
            task_name = request.data.get('task_name')

            # Check if any previous upload task is being executed
            if UploadStatus.objects.filter(user_id=user_id, task_completed=False).exists():
                return Response({"message": "A previous upload task is being executed. Please wait for it to finish"}, status=status.HTTP_403_FORBIDDEN)
            elif UploadStatus.objects.filter(table_name=task_name).exists():
                return Response({"message": "please select another name for the task"}, status=status.HTTP_409_CONFLICT)
            
            UploadStatus.objects.create(
                user_id=user_id,
                table_name=task_name,
                task_completed=False
            )
            
            # start upload task using celery worker
            start_upload_task.delay(task_name)

            return Response({
                "task_name": task_name
            })

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class PauseUploadView(APIView):

    def post(self, request, format=None):
        '''
        Pause ongoing upload task
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

class ResumeUploadView(APIView):

    def post(self, request, format=None):
        '''
        Resume a paused upload task
        '''

        try:
            task_name = request.data.get('task_name')
        
            # Set task status to run
            task_status = json.loads(redis_instance.get(task_name))
            task_status['status'] = 'run'
            redis_instance.set(task_name, json.dumps(task_status))

            # Run the background process for resuming the task
            resume_upload_task.delay(task_name)

            return Response({
                "task_name": task_name
            })

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class TerminateUploadView(APIView):

    def post(self, request, format=None):
        '''
        Terminate an ongoing upload task
        '''
        try:
            task_name = request.data.get('task_name')

            # Set task status to terminate
            task_status = json.loads(redis_instance.get(task_name))
            task_status['status'] = 'terminate'
            redis_instance.set(task_name, json.dumps(task_status))

            # Run the background process for rolling back the changes
            rollback_upload_task.delay(task_name)

            return Response({
                "task_name": task_name
            })
        
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
