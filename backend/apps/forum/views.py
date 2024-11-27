from rest_framework.views import APIView
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated

from apps.users.serializers import UserSerializer
from apps.forum.serializers import DiscussionForumSerializer, MessageDFSerializer, PublicationForumSerializer
from apps.forum.models import DiscussionForum,MessageDF, PublicationForum, FileDF,ImageDF
from apps.users.models import User
from rest_framework.parsers import MultiPartParser, FormParser
from datetime import datetime
import traceback

class PublicationForumListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        publicationObj = PublicationForum.objects.all().order_by('-id_publication_forum')
        publicationSer = PublicationForumSerializer(publicationObj, many=True, context={'user_id':request.user.id})
        return Response(publicationSer.data,status=200)

class PublicationForumFilterView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        publicationOjb = request.user.publicationF.all().order_by('-id_publication_forum')
        publicationSer = DiscussionForumSerializer(publicationOjb, many=True, context={'user_id':request.user.id})
        return Response(publicationSer.data,status=200)
    
class PublicationForumProfileView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request, publication_id):
        try:
            publicationObj = PublicationForum.objects.get(id_publication_forum=publication_id)
            publicationSer = PublicationForumSerializer(publicationObj, context={'user_id':request.user.id})
            return Response(publicationSer.data,status=200)
        except Exception as e:
            return Response({'erreur':str(e)},status=400)
        
    def delete(self, request, publication_id):
        try:
            publicationObj = PublicationForum.objects.get(id_publication_forum=publication_id)
            publicationObj.delete()
            return Response({'message':'publication supprimé avec succès'},status=200)
        except Exception as e:
            return Response({'erreur':str(e)},status=400)
        
class PublicationForumNewView(APIView):
    permission_classes=[IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        try:
            # request.data.keys = ["contenu","is_anonymous"]
            # request.FILES = ['images', 'files']
            if 'contenu'not in request.data:
                return Response({'erreur':'Veuillez verifier votre données'},status=400)
            sender = request.user
            files = request.FILES.getlist('files',[])
            images = request.FILES.getlist('images',[])
            print(request.FILES)
            publication_data = dict(request.data)
            publication_data['contenu']=request.data.get('contenu')
            publication_data['is_anonymous'] = request.data.get("is_anonymous", [False])[0]
            publication_data['user_id'] = request.user.id
            serializer = PublicationForumSerializer(data=publication_data, context=publication_data)
            serializer.is_valid(raise_exception=True)
            serializer_saved = serializer.save(sender=sender)
            publication = PublicationForum.objects.get(id_publication_forum=serializer_saved.id_publication_forum)
            
            for file in files:
                file_instance = FileDF.objects.create(file=file)
                publication.files.add(file_instance)
                print('file is added ...')

            for image in images:
                image_instance = ImageDF.objects.create(image=image)
                publication.images.add(image_instance)
                print('image added...')
                        
            publication.save()
            return Response({'message':'publication posté avec succès.'})

        except Exception as e:
            return Response({'erreur':str(e)},status=400)

class MessageDFNewView(APIView):
    permission_classes=[IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        #request.data.keys = ['contenu','is_anonymous', 'publicationF']
        #request.FILES = ['images','files']
        sender = request.user
        sender_id = request.user.id
        contenu = request.data.get('contenu')
        message_is_anonymous = request.data.get('is_anonymous',False)
        discussion_profile = "users/profiles/anonymous.png"if message_is_anonymous else request.user.profile
        
        discussionForum_created = DiscussionForum.objects.create(profile=discussion_profile, publicationF=PublicationForum.objects.get(id_publication_forum=request.data.get("publicationF")))
        discussionForum_created.membres.add(sender)
        discussion_id=discussionForum_created.id_discussion_forum

        try:
            discussion = DiscussionForum.objects.get(id_discussion_forum=discussion_id)
        except (User.DoesNotExist, DiscussionForum.DoesNotExist):
            return Response({"Erreur": "L'utilisateur ou la discussion n'existe pas."}, status=400)

        message_data = {
            'sender': sender_id,
            'discussionF': discussion.id_discussion_forum,
            'contenu': contenu,
            'is_anonymous': message_is_anonymous
        }
        files_data = request.FILES.getlist('files')
        images_data = request.FILES.getlist('images')
        message_serializer = MessageDFSerializer(
            data=message_data,
            context={'sender': sender, 'files_data': files_data, 'images_data': images_data}
        )
        if message_serializer.is_valid():
            message_serializer.save()
            return Response({"Message": "Le message a été créé avec succès."}, status=201)
        else:
            return Response({"Erreur": "Les données du message ne sont pas valides."}, status=400)

class MessageDFCommentView(APIView):
    permission_classes=[IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        #request.data.keys = ['contenu','is_anonymous', 'discussion']
        #request.FILES = ['images','files']
        sender = request.user
        sender_id = request.user.id
        contenu = request.data.get('contenu')
        

        try:
            discussion_id=request.data.get('discussion')
            discussion = DiscussionForum.objects.get(id_discussion_forum=discussion_id)
        except (User.DoesNotExist, DiscussionForum.DoesNotExist):
            return Response({"Erreur": "L'utilisateur ou la discussion n'existe pas."}, status=400)

        message_data = {
            'sender': sender_id,
            'discussionF': discussion.id_discussion_forum,
            'contenu': contenu,
            'is_anonymous':request.data.get('is_anonymous',False)
        }
        files_data = request.FILES.getlist('files')
        images_data = request.FILES.getlist('images')
        message_serializer = MessageDFSerializer(
            data=message_data,
            context={'sender': sender, 'files_data': files_data, 'images_data': images_data}
        )
        if message_serializer.is_valid():
            message_serializer.save()
            return Response({"Message": "Le message a été créé avec succès."}, status=201)
        else:
            return Response({"Erreur": "Les données du message ne sont pas valides."}, status=400)
        
class MessageDFResponseView(APIView):
    permission_classes=[IsAuthenticated]

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        #request.data.keys = ['discussion','contenu']
        #request.FILES = ['images','files']
        if any(key not in request.data.keys()for key in ['discussion','contenu']):
            return Response({'error':'Tous les attributs sont recquis'},status=400)
        sender = request.user
        sender_id = request.user.id
        discussion_id = request.data.get('discussion')
        contenu = request.data.get('contenu')

        try:
            discussion = DiscussionForum.objects.get(id_discussion_forum=discussion_id)
        except (User.DoesNotExist, DiscussionForum.DoesNotExist):
            return Response({"Erreur": "L'utilisateur ou la discussion n'existe pas."}, status=400)

        message_data = {
            'sender': sender_id,
            'discussionF': discussion.id_discussion_forum,
            'contenu': contenu
        }
        files_data = request.FILES.getlist('files')
        images_data = request.FILES.getlist('images')
        print(message_data)
        message_serializer = MessageDFSerializer(
            data=message_data,
            context={'sender': sender, 'files_data': files_data, 'images_data': images_data}
        )
        if message_serializer.is_valid():
            message_serializer.save()
            return Response({"Message": "Le message a été créé avec succès."}, status=201)
        else:
            return Response({"Erreur": "Les données du message ne sont pas valides."}, status=400)

class MessageDFProfileView(APIView):
    permission_classes=[IsAuthenticated]
    
    def delete(self, request, id_messageDF):
        try:
            messageObj = MessageDF.objects.get(id_messageDF=id_messageDF)
            if messageObj.sender!=request.user:
                return Response({'error':'Vous n\'avez pas la permission d\'effectuer cette operation'})
            messageObj.delete()
            return Response({"message":"message a été supprimé avec succès"},status=201)
        except MessageDF.DoesNotExist:
            return Response({"erreur": f"Message avec id {id_messageDF} est inexistant"},status=404)

class LikeMessageDFView(APIView):
    permission_classes=[IsAuthenticated]

    def put(self, request, message_id):
        try:
            sender = request.user
            message = MessageDF.objects.get(id_messageDF=message_id)
            if sender in message.likes.all():
                message.likes.remove(sender)
                return Response({"message": "Utilisateur retiré des likes avec succès."}, status=200)
            else:
                message.likes.add(sender)
                if sender in message.dislikes.all():
                    message.dislikes.remove(sender)
                return Response({"message": "Utilisateur ajouté aux likes avec succès."}, status=200)
        except MessageDF.DoesNotExist:
            return Response({'error': 'Message non trouvé'}, status=404)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=404)
        except Exception as e:
            print(e)
            return Response({'erreur': str(e)}, status=400)

class DislikeMessageDFView(APIView):
    permission_classes=[IsAuthenticated]

    def put(self, request, message_id):
        try:
            sender = request.user
            message = MessageDF.objects.get(id_messageDF=message_id)
            if sender in message.dislikes.all():
                message.dislikes.remove(sender)
                return Response({"message": "Utilisateur retiré des likes avec succès."}, status=200)
            else:
                message.dislikes.add(sender)
                if sender in message.likes.all():
                    message.likes.remove(sender)
                return Response({"message": "Utilisateur ajouté aux likes avec succès."}, status=200)
        except MessageDF.DoesNotExist:
            return Response({'error': 'Message non trouvé'}, status=404)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=404)
        except Exception as e:
            return Response({'erreur': str(e)}, status=400)

class LikePublicationFView(APIView):
    permission_classes=[IsAuthenticated]

    def put(self, request, publication_id):
        try:
            sender = request.user
            publicationF = PublicationForum.objects.get(id_publication_forum=publication_id)
            if sender in publicationF.likes.all():
                publicationF.likes.remove(sender)
                publicationF.save()
                return Response({"message": "Utilisateur retiré des likes avec succès."}, status=200)
            else:
                publicationF.likes.add(sender)
                if sender in publicationF.dislikes.all():
                    publicationF.dislikes.remove(sender)
                publicationF.save()
                return Response({"message": "Utilisateur ajouté aux likes avec succès."}, status=200)
        except MessageDF.DoesNotExist:
            return Response({'error': 'Message non trouvé'}, status=404)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=404)
        except Exception as e:
            print(e)
            return Response({'erreur': str(e)}, status=400)

class DislikePublicationFView(APIView):
    permission_classes=[IsAuthenticated]

    def put(self, request, publication_id):
        try:
            sender = request.user
            publicationF = PublicationForum.objects.get(id_publication_forum=publication_id)
            if sender in publicationF.dislikes.all():
                publicationF.dislikes.remove(sender)
                publicationF.save()
                return Response({"message": "Utilisateur retiré des likes avec succès."}, status=200)
            else:
                publicationF.dislikes.add(sender)
                if sender in publicationF.likes.all():
                    publicationF.likes.remove(sender)
                publicationF.save()
                return Response({"message": "Utilisateur ajouté aux likes avec succès."}, status=200)
        except MessageDF.DoesNotExist:
            return Response({'error': 'Message non trouvé'}, status=404)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=404)
        except Exception as e:
            return Response({'erreur': str(e)}, status=400)

class CommentPublicationView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def validate(self, data):
        try:
            keys = ['publication', 'contenu']
            if any(key not in data.keys()for key in keys):
                return False
            print(data)
            return PublicationForum.objects.filter(id_publication_forum=data['publication']).exists() and data['contenu'].strip()!=''
        except Exception :
            return False
    
    def post(self, request):
        try:
            # request.data.keys = ['publication', 'contenu']
            #request.FILES  = ['images', 'files']
            sender = request.user
            if not self.validate(request.data):
                return Response({'error':'Veuillez verifier vos données'}, status=400)
            new_discussion = DiscussionForum.objects.create(publicationF=PublicationForum.objects.get(id_publication_forum=request.data.get('publication')))
            new_discussion.membres.add(sender)
            new_discussion.save()
            new_message = MessageDF.objects.create(discussionF=new_discussion, sender=sender, contenu=request.data.get('contenu'))
            files, images = request.FILES.getlist('files'), request.FILES.getlist('images')
            for file in files:
                new_file = FileDF.objects.create(file)
                new_message.files.add(new_file)
                new_message.save()
                print('file added .....')
            for image in images:
                new_image = ImageDF.objects.create(image)
                new_message.files.add(new_image)
                new_message.save()
                print('image added .....')
            return Response({'message':'Commentaire ajouté avec succès..'})
        except Exception as e:
            print(e)
            return Response({'error':str(e)},status=400)