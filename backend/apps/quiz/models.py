from django.db import models
from apps.users.models import User, default_created_at

class Quiz(models.Model):
    CATEGORY_CHOICES = [
        ('mst','MST'),
        ('grossesse','Grossesse'),
        ('menstruation','Menstruation'),
        ('contraception','Methode contraceptive')
    ]
    id_quiz = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    question_text = models.TextField()
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)

    def __str__(self):
        return f"{self.title} - Question : {self.question_text}"

    class Meta:
        db_table = 'quiz'

class ResponseQuiz(models.Model):
    id_response_quiz = models.AutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='responses')
    content = models.TextField()
    is_correct = models.BooleanField(default=False)
    rank = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Réponse : {self.content} (Correct : {self.is_correct}, Rang : {self.rank})"

    class Meta:
        db_table = 'responsequiz'

class QuizFinished(models.Model):
    id_quiz_finished = models.AutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="quiz_finished")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz_finished")
    created_at = models.DateTimeField(default=default_created_at)
    
    def __str__(self):
        return str(self.quiz)+" - "+self.user
    
    class Meta:
        db_table = "quiz_finished"