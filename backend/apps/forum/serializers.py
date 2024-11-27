from rest_framework import serializers

from django.conf import settings
from django.utils import timezone

from apps.users.models import User
from apps.users.serializers import UserSerializer
from apps.forum.models import DiscussionForum,MessageDF,FileDF,ImageDF, PublicationForum

from datetime import timedelta,datetime
import calendar

class FileDFSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = FileDF
        fields = ['url', 'name', 'type']

    def get_url(self, obj):
        return f"{settings.BASE_URL}api{obj.file.url}" if obj.file else None
    
    def get_name(self, obj):
        return obj.file.name.split('/')[-1] if obj.file else None
    
    def get_type(self, obj):
        return obj.file.name.split('.')[-1] if obj.file else None
    
class ImageDFSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = ImageDF  # Remplacez par le modèle correct pour les images
        fields = ['url', 'name', 'type']

    def get_url(self, obj):
        return f"{settings.BASE_URL}api{obj.image.url}" if obj.image else None
    
    def get_name(self, obj):
        return obj.image.name.split('/')[-1] if obj.image else None
    
    def get_type(self, obj):
        return obj.image.name.split('.')[-1] if obj.image else None

class DiscussionForumSerializer(serializers.ModelSerializer):
    membres = UserSerializer(many=True,read_only=True)
    responses = serializers.SerializerMethodField()
    responses_number = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()
    time_elapsed = serializers.SerializerMethodField()
    first = serializers.SerializerMethodField()
    
    class Meta:
        model = DiscussionForum
        fields = ['id_discussion_forum','membres','responses', 'responses_number', 'sender', 'first', 'publicationF', 'time_elapsed','created_at']

    def get_responses(self, obj):
        messages = obj.messages.all()
        if len(messages)<=1:
            return []
        return MessageDFSerializer(messages[1:], many=True, context={'user_id':self.context.get('user_id',None)}).data
    
    def get_first(self, obj):
        messages = obj.messages.all()
        if len(messages)==0:
            obj.delete()
            return {}
        return MessageDFSerializer(messages.first(), context={'user_id':self.context.get('user_id',None)}).data
    
    def get_time_elapsed(self, obj):
        current_time = timezone.localtime(timezone.now())
        time_difference = current_time - obj.created_at
        current_year = current_time.year
        current_month = current_time.month
        days_in_month = calendar.monthrange(current_year, current_month)[1]

        if time_difference < timedelta(minutes=1):
            return "à l'instant"
        elif time_difference < timedelta(hours=1):
            minutes = int(time_difference.total_seconds() / 60)
            return f"{minutes} min"
        elif time_difference < timedelta(days=1):
            hours = int(time_difference.total_seconds() / 3600)
            return f"{hours} h"
        elif time_difference < timedelta(days=days_in_month):
            days = int(time_difference.total_seconds() / 86400)
            return f"{days} j"
        elif time_difference < timedelta(days=365):
            months = int(time_difference.total_seconds() / 2592000)
            return f"{months} mois"
        else:
            years = int(time_difference.total_seconds() / 31536000)
            return f"{years} ans"
    
    def get_responses_number(self, obj):
        messages = obj.messages.all()
        if len(messages)<=1:
            return 0
        return messages.count()-1
    
    def get_sender(self, obj):
        anonymous_user, created = User.objects.get_or_create(
            email="anonymous@example.com",
            defaults={
                "name": "Anonymous",
                "sexe": "I",
                "is_active": True,
                "profile":"users/profilee/anonymous.png",
                "birth_date":datetime.strptime("1000-01-01","%Y-%m-%d")
            },
        )
        if obj.messages.all().count()==0:
            obj.delete()
            return UserSerializer(anonymous_user).data
        message_first = obj.messages.all().first()
        if message_first.is_anonymous:
            return UserSerializer(anonymous_user).data
        return UserSerializer(message_first.sender).data
    
    def to_representation(self, instance):
        detail = self.context.get('detail', False)
        displayMessage = self.context.get('messages', True)
        representation = super().to_representation(instance)
        if not detail:
            representation.pop('membres', None)
        if not displayMessage:
            representation.pop('messages')
        return representation

class PublicationForumSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    comments_number = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()
    likes_number = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    dislikes_number = serializers.SerializerMethodField()
    time_elapsed = serializers.SerializerMethodField()
    images = ImageDFSerializer(many=True,read_only=True)
    files = FileDFSerializer(many=True,read_only=True)
    
    
    class Meta:
        model = PublicationForum
        fields = ['id_publication_forum','comments', 'comments_number', 'contenu', 'images','files', 'sender', 'likes', 'dislikes', 'likes_number','dislikes_number','time_elapsed','created_at']

    def get_comments(self, obj):
        print('get comments...')
        comments = obj.comments.all()
        if len(comments)<1:
            return []
        return DiscussionForumSerializer(comments, many=True, context={'user_id':self.context.get('user_id',None)}).data
    
    def get_likes_number(self, obj):
        return obj.likes.all().count()
    
    def get_likes(self,obj):
        return [u.id for u in obj.likes.all()]
    
    def get_dislikes(self,obj):
        return [u.id for u in obj.dislikes.all()]
    
    def get_time_elapsed(self, obj):
        current_time = timezone.localtime(timezone.now())
        time_difference = current_time - obj.created_at
        current_year = current_time.year
        current_month = current_time.month
        days_in_month = calendar.monthrange(current_year, current_month)[1]

        if time_difference < timedelta(minutes=1):
            return "à l'instant"
        elif time_difference < timedelta(hours=1):
            minutes = int(time_difference.total_seconds() / 60)
            return f"{minutes} min"
        elif time_difference < timedelta(days=1):
            hours = int(time_difference.total_seconds() / 3600)
            return f"{hours} h"
        elif time_difference < timedelta(days=days_in_month):
            days = int(time_difference.total_seconds() / 86400)
            return f"{days} j"
        elif time_difference < timedelta(days=365):
            months = int(time_difference.total_seconds() / 2592000)
            return f"{months} mois"
        else:
            years = int(time_difference.total_seconds() / 31536000)
            return f"{years} ans"
    
    def get_dislikes_number(self, obj):
        return obj.dislikes.all().count()
    
    def get_comments_number(self, obj):
        return obj.comments.all().count()
    
    def get_sender(self, obj):
        if obj.is_anonymous:
            anonymous_user, created = User.objects.get_or_create(
                email="anonymous@example.com",
                defaults={
                    "name": "Anonymous",
                    "sexe": "I",
                    "is_active": True,
                    "profile":"users/profilee/anonymous.png",
                    "birth_date":datetime.strptime("1000-01-01","%Y-%m-%d")
                },
            )
            return UserSerializer(anonymous_user).data
        return UserSerializer(obj.sender).data
    
    def to_representation(self, instance):
        user_id = self.context.get('user_id',None)
        representation = super().to_representation(instance)
        if user_id is not None:
            representation['is_liked'] = user_id in representation['likes']
            representation['is_disliked'] = user_id in representation['dislikes']
        return representation

class MessageDFSerializer(serializers.ModelSerializer):
    images = ImageDFSerializer(many=True, read_only=True)
    files = FileDFSerializer(many=True, read_only=True)
    sender = UserSerializer(read_only=True)
    time_elapsed = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    likes_number = serializers.SerializerMethodField()
    dislikes_number = serializers.SerializerMethodField()

    class Meta:
        model = MessageDF
        fields = ['id_messageDF','discussionF','contenu','sender','images','files','likes_number','is_anonymous','likes','dislikes_number','dislikes','time_elapsed','created_at']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user_id = self.context.get('user_id',None)
        representation['profile_sender'] = representation['sender']['profile_url']
        if representation['is_anonymous']:
            anonymous_user, created = User.objects.get_or_create(
                email="anonymous@example.com",
                defaults={
                    "name": "Anonymous",
                    "sexe": "I",
                    "is_active": True,
                    "profile":"users/profilee/anonymous.png",
                    "birth_date":datetime.strptime("1000-01-01","%Y-%m-%d")
                },
            )
            representation['sender']=UserSerializer(anonymous_user).data
        if user_id is not None:
            representation['is_liked'] = user_id in representation['likes']
            representation['is_disliked'] = user_id in representation['dislikes']
        return representation

    def get_time_elapsed(self, obj):
        current_time = timezone.localtime(timezone.now())
        time_difference = current_time - obj.created_at
        current_year = current_time.year
        current_month = current_time.month
        days_in_month = calendar.monthrange(current_year, current_month)[1]

        if time_difference < timedelta(minutes=1):
            return "à l'instant"
        elif time_difference < timedelta(hours=1):
            minutes = int(time_difference.total_seconds() / 60)
            return f"{minutes} min"
        elif time_difference < timedelta(days=1):
            hours = int(time_difference.total_seconds() / 3600)
            return f"{hours} h"
        elif time_difference < timedelta(days=days_in_month):
            days = int(time_difference.total_seconds() / 86400)
            return f"{days} j"
        elif time_difference < timedelta(days=365):
            months = int(time_difference.total_seconds() / 2592000)
            return f"{months} mois"
        else:
            years = int(time_difference.total_seconds() / 31536000)
            return f"{years} ans"

    def get_likes(self, obj):
        return [u.id for u in obj.likes.all()]
    
    def get_likes_number(self,obj):
        return obj.likes.all().count()
    
    def get_dislikes(self, obj):
        return [u.id for u in obj.dislikes.all()]
    
    def get_dislikes_number(self,obj):
        return obj.dislikes.all().count()
    
    def create(self, validated_data):
        if 'sender' in self.context:
            validated_data['sender'] = self.context.get('sender')
        files = self.context.get('files_data', [])
        images = self.context.get('images_data', [])
        messageDF = MessageDF.objects.create(**validated_data)
        for file in files:
            file_instance = FileDF.objects.create(file=file)
            messageDF.files.add(file_instance)
            print('file added ....')

        for image in images:
            image_instance = ImageDF.objects.create(image=image)
            messageDF.images.add(image_instance)
            print('image added...')

            
        return messageDF
