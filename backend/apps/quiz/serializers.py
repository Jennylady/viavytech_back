from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status

from apps.quiz.models import Quiz, ResponseQuiz, QuizFinished

class ResponseQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponseQuiz
        fields = ['id_response_quiz', 'content', 'is_correct', 'rank', 'quiz']

class QuizSerializer(serializers.ModelSerializer):
    responses = ResponseQuizSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['id_quiz', 'title', 'question_text', 'category', 'responses']

    def create(self, validated_data):
        # response_data.keys = ['is_correct', 'rank','correct']
        responses_data = validated_data.pop('responses', [])
        quiz = super().create(validated_data)

        for response_data in responses_data:
            Response.objects.create(quiz=quiz, **response_data)

        return quiz
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        not_finished_only = self.context.get('not_finished_only', False)
        user = self.context.get('user')

        if not_finished_only and user:
            if QuizFinished.objects.filter(quiz=instance, user=user).exists():
                return None

        return representation