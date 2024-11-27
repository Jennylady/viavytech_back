from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('secretadmin/', admin.site.urls),
    path('api/',include('apps.users.urls')),
    path('api/',include('apps.forum.urls')),
    path('api/',include('apps.menstruation.urls')),
    path('api/',include('apps.chatbot.urls')),
    path('api/', include('apps.quiz.urls')),
]
