from django.urls import path
from .views import *

urlpatterns = [
    path('', Homepage, name='homepage'),
    path('tasks/',GetAllTasks.as_view(),name="tasks"),
    path('all-tasks/',AllTasks,name="all-tasks"),
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginHandler.as_view(), name='login'),
    path('logout/', LogoutHandler, name='logout'),
    path('create-task/',TaskAPI.as_view(),name="create-task"),
    path('403/',AccessDenied403,name="403"),
    path('task/<int:task_id>/',EditTask,name="modify-task"),
    path('task/<int:task_id>/api/',ModifyTaskAPI.as_view(),name="modify-task-api"),
    path('read-task/<int:task_id>/',ReadTask,name="read-task"),
]
