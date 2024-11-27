from rest_framework import serializers

from apps.chatbot.models import Conversation, MessageChat

class MessageChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageChat
        fields = ['id_message_chat', 'contenu', 'conversation', 'from_user', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id_conversation', 'user', 'titre', 'created_at', 'messages']

    def get_messages(self, obj):
        messages = obj.messages.all() 
        return MessageChatSerializer(messages, many=True).data
