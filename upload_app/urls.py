from django.urls import path
from .views import StartUploadView, PauseUploadView, ResumeUploadView, TerminateUploadView

urlpatterns = [
    path('start/', StartUploadView.as_view()),
    path('pause/', PauseUploadView.as_view()),
    path('resume/', ResumeUploadView.as_view()),
    path('terminate/', TerminateUploadView.as_view())
]