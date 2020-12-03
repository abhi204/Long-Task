from django.urls import path
from .views import StartDownloadView, PauseDownloadView, ResumeDownloadView, TerminateDownloadView, DownloadProgressView

urlpatterns = [
    path('start/', StartDownloadView.as_view()),
    path('pause/', PauseDownloadView.as_view()),
    path('resume/', ResumeDownloadView.as_view()),
    path('terminate/', TerminateDownloadView.as_view()),
    path('progress/', DownloadProgressView.as_view())
]