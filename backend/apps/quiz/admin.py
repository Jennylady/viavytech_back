from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from apps.quiz.models import Quiz, ResponseQuiz

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id_quiz', 'title', 'category', 'question_text')
    search_fields = ('title', 'category')
    list_filter = ('category',)
    actions = ['modifier_le_quiz']
    ordering = ('-id_quiz',)

    def modifier_le_quiz(self, request, queryset):
        quiz = queryset.first()
        if quiz:
            url = reverse('admin:quiz_quiz_change', args=[quiz.id_quiz])
            return HttpResponseRedirect(url)

    modifier_le_quiz.short_description = "Modifier le quiz sélectionné"

@admin.register(ResponseQuiz)
class ResponseQuizAdmin(admin.ModelAdmin):
    list_display = ('id_response_quiz', 'quiz', 'content', 'is_correct', 'rank')
    list_filter = ('quiz__category',)
    search_fields = ('content', 'quiz__title')
    actions = ['modifier_la_reponse']

    def modifier_la_reponse(self, request, queryset):
        response = queryset.first()
        if response:
            url = reverse('admin:quiz_responsequiz_change', args=[response.id_response_quiz])
            return HttpResponseRedirect(url)

    modifier_la_reponse.short_description = "Modifier la réponse sélectionnée"
