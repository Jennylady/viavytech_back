# apps/quiz/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('quiz/', views.QuizListView.as_view(), name='quiz-list'),
    path('quiz/add/', views.AddQuizView.as_view(), name='add-quiz'),
    path('quiz/submit/<int:quiz_id>/', views.SubmitQuizView.as_view(), name='submit-quiz'),
]
