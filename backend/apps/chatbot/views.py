from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.chatbot.models import Conversation, MessageChat
from apps.chatbot.serializers import ConversationSerializer, MessageChatSerializer

from helpers.helper import helloworld, messageChatRASA
import random
import traceback


class ConversationFilterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            conversations = Conversation.objects.filter(user=request.user)
            serializer = ConversationSerializer(conversations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=400)
        
class ConversationProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(id_conversation=conversation_id)
            if conversation.user.id != request.user.id:
                return Response({'erreur':'Vous n\'avez pas la permission de faire cette opération'},status=401)
            serializer = ConversationSerializer(conversation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=400)
        
class ConversationNewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data

            data['user'] = request.user.id

            serializer = ConversationSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=400)

class MessageChatNewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # request.data.keys = ['conversation','contenu']
            print(request.data)
            data = request.data
            conversation_id = data.get('conversation')
            contenu = data.get('contenu')
            from_user = data.get('from_user', True)

            try:
                conversation = Conversation.objects.get(id_conversation=conversation_id)
            except Conversation.DoesNotExist:
                return Response(
                    {"error": "Conversation introuvable ou non autorisée."},
                    status=status.HTTP_404_NOT_FOUND
                )

            messageChat_response = messageChatRASA(contenu, request.user.name, debug=1)
            
            message_data = {
                "conversation": conversation.id_conversation, 
                "contenu": contenu,
                "from_user": from_user
            }
            serializer = MessageChatSerializer(data=message_data)
            if serializer.is_valid():
                serializer.save()
                if len(messageChat_response)>0:
                    message_bot = messageChat_response[0]['text']
                else:
                    message_bot = random.choices(['Veuillez donner plus d\'information sur ce sujet!', 'Donnez-moi plus de clarification', 'Expliquez-moi d\'avantages', 'Ceci n\'est pas encore dans mes competences','Ce sujet ne m\'est pas familier, désolé!'])
                print(message_bot)
                MessageChat.objects.create(conversation=conversation,contenu=message_bot,from_user=False)
                return Response({"bot_response":message_bot}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(traceback.format_exc())
            return Response({'error':str(e)},status=400)
