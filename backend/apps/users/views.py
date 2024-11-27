from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import TokenError
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.users.serializers import UserSerializer, LoginSerializer, RegisterSerializer
from apps.users.models import User

from dotenv import load_dotenv
import traceback

load_dotenv()


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request:Request):
        serializer = UserSerializer(request.user, context={'request': request})
        user = serializer.data
        if not user['is_active']:
            return Response({'error': 'Accès refusé: votre compte doit être actif. Veuillez vous connecter pour continuer.'}, status=403)
        return Response(user, status=200)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request:Request):
        try:
            user = User.objects.get(id=request.user.id)
            user.is_active = False
            user.save()
            return Response({'message':'Utilisateur déconnecté avec succès.'}, status=200)
        except User.DoesNotExist:
            return Response({'erreur':"Utilisateur non trouvé"}, status=404)

class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        # request.data.keys = ['email', 'password']
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            return Response({"erreur":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def check_if_user_exist(self, email):
        return User.objects.filter(email=email).exists()
    
    def validate_data(self, data):
        try:
            keys = ['name','email','password','sexe', 'birth_date', 'phone_number']
            if any(key not in data.keys() for key in keys):
                return False
            return True
        except Exception as e:
            return False
    
    
    def post(self, request):
        # request.data.keys = ['name','email','password','sexe', 'phone_number', 'proffession_domaine', 'birth_date']
        try:
            user_data = request.data
            print(request.data)
            if not self.validate_data(user_data):
                return Response({'erreur':'Tous les attributs sont requis'}, status=status.HTTP_400_BAD_REQUEST)
            birth_date = request.data['birth_date'].replace('/','-')
            user_data['birth_date'] = birth_date
            if self.check_if_user_exist(request.data['email']):
                return Response({'erreur':'email existant'},status=400)
            if "profession_domaine"not in user_data:
                user_data["profession_domaine"]="Inconu"
            if user_data.get('sexe', 'I').lower() not in ['masculin', 'feminin']: user_data['sexe'] = 'I'
            else: user_data['sexe'] = user_data['sexe'].strip()[0].upper()
            
            serializer = RegisterSerializer(data=user_data)
            if serializer.is_valid(raise_exception=True):
                # serializer.save()
                return Response({"email":serializer.validated_data["email"]}, status=status.HTTP_201_CREATED)
            else:
                return Response({'erreur':'erreur de serialisation'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(traceback.format_exc())
            return Response({"erreur":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        