from django.urls import path
from . import views

urlpatterns = [
    path('reporters/', views.reporter_views, name='reporter_views'),
    path('issues/', views.issue_views, name='issue_views'),
]
