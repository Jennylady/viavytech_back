from django.db import models
from apps.users.models import User, default_created_at

class Conversation(models.Model):
    id_conversation = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations")
    titre = models.CharField(max_length=100,default='')
    created_at = models.DateTimeField(default=default_created_at())
    
    def __str__(self):
        return f"conversation:{self.id_conversation} - {self.user}"
    
    class Meta:
        db_table = "conversationChat"
        
class MessageChat(models.Model):
    id_message_chat = models.AutoField(primary_key=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    contenu = models.CharField(max_length=250)
    from_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=default_created_at())
    
    def __str__(self):
        return f"{self.Conversation} - {self.contenu}"
    
    class Meta:
        db_table = "messageChat"