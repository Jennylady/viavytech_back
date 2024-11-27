from django.urls import path

from apps.quiz.views import QuizListFilterView, QuizListView, SubmitQuizResponseView

urlpatterns = [
    path('quiz/list/', QuizListView.as_view(),name="quiz_list"),# GET
    path('quiz/list/filter/<str:category>/', QuizListFilterView.as_view(),name='quiz_filter'),#GET
    path('quiz/answer/', SubmitQuizResponseView.as_view(), name='submit response'),# POST
]
