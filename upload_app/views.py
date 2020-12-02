import uuid, json
from .tasks import start_upload_task, resume_upload_task, rollback_upload_task
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from shared.helpers import redis_instance


# Create your views here.
class StartUploadView(APIView):

    def get(self, request, format=None):
        '''
        Starts upload task and returns task id
        '''

        # generate new task id
        task_id = str(uuid.uuid4())

        # start upload task using celery worker
        start_upload_task.delay(task_id)

        return Response({
            "task_id": task_id
        })

class PauseUploadView(APIView):

    def post(self, request, format=None):
        '''
        Pause ongoing upload task
        '''

        try:
            task_id = request.data.get('task_id')
            
            # set task status to paused
            task_status = json.loads(redis_instance.get(task_id))
            task_status['status'] = 'pause'
            redis_instance.set(task_id, json.dumps(task_status))

            return Response({
                "task_id": task_id
            })

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ResumeUploadView(APIView):

    def post(self, request, format=None):
        '''
        Resume a paused upload task
        '''

        try:
            task_id = request.data.get('task_id')
        
            # Set task status to run
            task_status = json.loads(redis_instance.get(task_id))
            task_status['status'] = 'run'
            redis_instance.set(task_id, json.dumps(task_status))

            # Run the background process for resuming the task
            resume_upload_task.delay(task_id)

            return Response({
                "task_id": task_id
            })

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class TerminateUploadView(APIView):

    def post(self, request, format=None):
        '''
        Terminate an ongoing upload task
        '''
        try:
            task_id = request.data.get('task_id')

            # Set task status to terminate
            task_status = json.loads(redis_instance.get(task_id))
            task_status['status'] = 'terminate'
            redis_instance.set(task_id, json.dumps(task_status))

            # Run the background process for rolling back the changes
            rollback_upload_task.delay(task_id)

            return Response({
                "task_id": task_id
            })
        
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
