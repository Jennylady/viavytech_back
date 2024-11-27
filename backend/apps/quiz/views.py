from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.quiz.models import Quiz, ResponseQuiz
from apps.quiz.serializers import QuizSerializer

class QuizListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        quizzes = Quiz.objects.all()
        serializer_data = QuizSerializer(quizzes, many=True).data
        if len(serializer_data)>10:
            return Response(serializer_data[:10])
        return Response(serializer_data)

class QuizListFilterView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, category):
        try:
            quizzes = Quiz.objects.filter(category=category)
            serializer_data = QuizSerializer(quizzes, many=True,context={'not_finished_only': True, 'user': request.user}).data
            if len(serializer_data)>10:
                return Response(serializer_data[:10])
            return Response(serializer_data)
        except Exception as e:
            return Response({'erreur':str(e)},status=400)

class SubmitQuizResponseView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # request.data.keys = ['id_quiz', 'answer_rank']
        try:
            quiz = Quiz.objects.get(id_quiz=request.data['id_quiz'])
            response = quiz.responses.filter(rank=request.data['answer_rank']).first()
            return Response({'answer_is_correct':response.is_correct, 'expected_response':quiz.responses.filter(is_correct=True).first()})
        except (Quiz.DoesNotExist, Exception) as e:
            return Response({'error': str(e)}, status=400)
        
