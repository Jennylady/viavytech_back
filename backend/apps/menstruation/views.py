from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.menstruation.models import Woman, Menstruation, Ovulation, Symptom, Notification
from apps.menstruation.serializers import WomanSerializer, MenstruationSerializer, OvulationSerializer, SymptomSerializer, SymptomLinkWomanSerializer
from apps.menstruation.permissions import IsAuthenticatedWoman
from django.contrib.auth.models import AnonymousUser
from helpers.helper import send_sms

from datetime import timedelta, datetime
import traceback
import os
import random

PRE_MENSTRUATION_TWO_DAYS = [
    "Votre règle débutera dans 2 jours, pensez à vous préparer en achetant des serviettes hygiéniques et en aménageant du temps pour vous reposer.",
    "C'est bientôt le début de votre cycle menstruel dans deux jours, préparez vos affaires et prenez soin de vous.",
    "Deux jours avant vos règles, il est temps de penser à vos besoins essentiels : repos, hydratation et protections hygiéniques.",
    "N'oubliez pas que vos règles commencent dans 2 jours. Soyez prête, organisez-vous pour éviter les imprévus."
]

PRE_MENSTRUATION_ONE_DAY = [
    "Votre règle va commencer demain, êtes-vous prête ? Assurez-vous d'avoir tout ce dont vous avez besoin, et courage !",
    "Demain marque le début de votre cycle menstruel. Préparez vos serviettes hygiéniques et reposez-vous ce soir.",
    "À un jour de vos règles, pensez à bien vous hydrater et à prendre soin de vous mentalement et physiquement.",
    "Vos règles commencent demain, une bonne organisation aujourd'hui vous aidera à être plus sereine demain."
]

MENSTRUATION_MESSAGES = [
    "Prenez soin de vous et accordez-vous des moments de repos.",
    "N'oubliez pas de boire beaucoup d'eau pour rester hydratée.",
    "Pour soulager les douleurs, utilisez une bouillotte ou essayez des exercices doux.",
    "Une alimentation riche en fer peut vous aider à compenser les pertes, pensez aux légumes verts et aux viandes maigres.",
    "Évitez les activités physiques intenses, privilégiez le repos et les mouvements légers.",
    "Si vous en ressentez le besoin, parlez à vos proches ou demandez de l'aide pour vos tâches quotidiennes."
]

PRE_OVULATION_MESSAGES = [
    "Profitez de cette période pour planifier vos projets ou activités importantes.",
    "C'est un moment idéal pour renforcer votre énergie avec une alimentation équilibrée.",
    "Faites des exercices réguliers pour maintenir un bon niveau d'énergie.",
    "Gardez une attitude positive et concentrez-vous sur vos objectifs.",
    "Essayez des infusions naturelles pour équilibrer vos hormones.",
    "Cette période est parfaite pour clarifier vos intentions et vous organiser mentalement."
]

FERTILITY_MESSAGES = [
    "C'est une période idéale pour la conception. Soyez attentive aux signes que votre corps vous envoie.",
    "Réduisez le stress et prenez soin de votre bien-être émotionnel pour maximiser vos chances.",
    "Partagez vos intentions et émotions avec votre partenaire pour un soutien mutuel.",
    "Adoptez un mode de vie sain en dormant bien et en mangeant équilibré.",
    "Pensez aux vitamines et minéraux pour soutenir votre santé reproductive.",
    "C'est une période spéciale, soyez à l'écoute de vous-même et profitez du moment."
]

PRE_FERTILITY_TWO_DAYS = [
    "Dans deux jours, votre période de fertilité débutera. Préparez-vous en adoptant une alimentation équilibrée et en réduisant le stress.",
    "Votre fenêtre fertile commence dans deux jours, soyez attentive à votre corps et reposez-vous bien d'ici là.",
    "C'est bientôt le début de votre période fertile, prenez le temps de vous concentrer sur votre bien-être.",
    "Dans deux jours, vous entrez dans une phase importante de votre cycle. Planifiez en conséquence."
]

PRE_FERTILITY_ONE_DAY = [
    "Demain commence votre fenêtre fertile. Assurez-vous de vous sentir bien et de garder une routine saine.",
    "À un jour de votre période fertile, c'est le moment de vous préparer et de communiquer avec votre partenaire.",
    "Votre fertilité augmente demain. Prenez soin de vous et écoutez les signaux de votre corps.",
    "Soyez prête pour votre fenêtre fertile qui débute demain. Adoptez une attitude positive et restez détendue."
]

POST_OVULATION_MESSAGES = [
    "Prenez le temps de vous reposer et de récupérer après cette phase importante.",
    "Maintenez une alimentation équilibrée avec des nutriments essentiels pour un cycle en bonne santé.",
    "Surveillez vos symptômes et notez-les pour une meilleure compréhension de votre cycle.",
    "Pratiquez des exercices doux pour favoriser la détente et l'équilibre.",
    "C'est une période parfaite pour méditer et prendre du temps pour vous.",
    "Préparez-vous à entrer dans la prochaine phase avec sérénité et confiance."
]


def get_notification(woman):
    menstruations = woman.menstruations.all().order_by('-start_date')
    if menstruations.count()==0:
        return "Veuiller nous informer de votre dérnier règle pour avoir un peu plus de prevision sur votre cycle menstruel.Sexual Education vous remercie."
    last_period = menstruations.first().start_date
    
    predicted_ovulation_date = last_period + timedelta(days=woman.get_cycle() - 14)
    fertility_window_start = predicted_ovulation_date - timedelta(days=4)
    fertility_window_end = predicted_ovulation_date + timedelta(days=3)
    last_menstruation = woman.menstruations.order_by('-start_date').first()
    if not last_menstruation:
        return "Veuiller nous informer de votre dérnier règle pour avoir un peu plus de prevision sur votre cycle menstruel.Sexual Education vous remercie."
    
    predicted_start = last_menstruation.start_date + timedelta(days=woman.get_cycle())
    predicted_end_date_duration = predicted_start+timedelta(days=int(woman.average_menstruation_duration))
    
    today = datetime.now().date()
    if today.strftime('%Y-%m-%d')in [(m.start_date-timedelta(days=2)).strftime('%Y-%m-%d') for m in woman.menstruations.all().order_by('start_date')]+[(predicted_start-timedelta(days=2)).strftime('%Y-%m-%d')]:
        current_phase = "normal"
        advice = random.choice(PRE_MENSTRUATION_TWO_DAYS)
    elif today.strftime('%Y-%m-%d')in [(m.start_date-timedelta(days=1)).strftime('%Y-%m-%d') for m in woman.menstruations.all().order_by('start_date')]+[(predicted_start-timedelta(days=1)).strftime('%Y-%m-%d')]:
        current_phase = "normal"
        advice = random.choice(PRE_MENSTRUATION_ONE_DAY)
    elif last_menstruation.start_date <= today <= last_menstruation.end_date or predicted_start<=today<=predicted_end_date_duration:
        current_phase = "menstruation"
        advice = random.choice(MENSTRUATION_MESSAGES)
    elif last_menstruation.end_date < today < fertility_window_start:
        current_phase = "normal"
        advice = random.choice(PRE_OVULATION_MESSAGES)
    elif fertility_window_start <= today <= fertility_window_end:
        current_phase = "fertile"
        advice = random.choice(FERTILITY_MESSAGES)
    else:
        current_phase = "normal"
        advice = random.choice(POST_OVULATION_MESSAGES)
    return advice

class WomanLastInfoView(APIView):
    permission_classes = [IsAuthenticatedWoman]
    
    def get(self, request):
        try:
            woman = request.woman
            woman = WomanSerializer(woman, context={'last_info':True}).data
            return Response(woman, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)

class WomanInfoView(APIView):
    permission_classes = [IsAuthenticatedWoman]

    def get(self, request):
        try:
            woman = WomanSerializer(request.woman).data
            return Response(woman, status=status.HTTP_200_OK)
        except Menstruation.DoesNotExist:
            return Response({'detail': 'Menstruation records not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MenstruationListView(APIView):
    permission_classes = [IsAuthenticatedWoman]

    def get(self, request):
        try:
            woman = WomanSerializer(request.woman, context={'only_menstruations':True}).data
            return Response(woman, status=status.HTTP_200_OK)
        except Menstruation.DoesNotExist:
            return Response({'detail': 'Menstruation records not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class MenstruationNew(APIView):
    permission_classes = [IsAuthenticatedWoman]
    
    def validate(self, data):
        try:
            keys=['start_date','menstruation_duration']
            if any(key not in data.keys()for key in keys):
                return False
            start_date = datetime.strptime(data['start_date'],'%Y-%m-%d')
            if start_date>datetime.now():
                return False
            return True
        except Exception:
            return False

    # request.data.keys = ['start_date', 'menstruation_duration']
    def post(self, request):
        try:
            if not self.validate(request.data):
                return Response({'error':'veuillez verifier votre donné'},status=400)
            woman = request.woman
            start_date = datetime.strptime(request.data['start_date'], '%Y-%m-%d').date()

            woman.update_average_menstruation_length()

            duration = request.data.get('menstruation_duration',woman.average_menstruation_duration)
            end_date = start_date +timedelta(days=int(duration)) if duration is not None else start_date + timedelta(days=woman.average_menstruation_duration)
            data = {
                'start_date': start_date,
                'end_date': end_date
                }

            serializer = MenstruationSerializer(data=data)
            if serializer.is_valid():
                menstruation = serializer.save(woman=woman)
                woman.last_period_date = woman.menstruations.order_by('-start_date').first().start_date
                woman.update_average_menstruation_length()
                woman.update_average_cycle_length()
                woman.save()
                
                predicted_ovulation_date = start_date + timedelta(days=woman.average_cycle_length - 14)
                fertility_window_start = predicted_ovulation_date - timedelta(days=5)
                fertility_window_end = predicted_ovulation_date + timedelta(days=1)
                
                Ovulation.objects.create(
                    woman=woman,
                    predicted_ovulation_date=predicted_ovulation_date,
                    fertility_window_start=fertility_window_start,
                    fertility_window_end=fertility_window_end
                )
                
                notification_message = get_notification(woman)
                Notification.objects.create(
                    woman=woman,
                    message=notification_message
                )
                send_sms(woman.user.phone_number, notification_message)
                    
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            print('serializer is not valid...')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MenstruationPredictView(APIView):
    permission_classes = [IsAuthenticatedWoman]

    def get(self, request):
        try:
            last_menstruation = request.woman.menstruations.order_by('-start_date').first()
            if not last_menstruation:
                return Response({'detail': 'No menstruation data available for prediction'}, status=status.HTTP_404_NOT_FOUND)
            
            predicted_start = last_menstruation.start_date + timedelta(days=request.woman.average_cycle_length)
            predicted_end_date_duration = predicted_start+timedelta(days=int(request.woman.average_menstruation_duration))
            return Response({'predicted_start_date': predicted_start, 'predicted_end_date_duration':predicted_end_date_duration}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class OvulationPredictView(APIView):
    permission_classes = [IsAuthenticatedWoman]

    def get(self, request):
        try:
            last_period = request.woman.menstruations.order_by('-start_date').first().start_date
            if not last_period:
                return Response({'detail': 'Last period date not available'}, status=status.HTTP_404_NOT_FOUND)
            
            predicted_ovulation_date = last_period + timedelta(days=request.woman.average_cycle_length - 14)
            fertility_window_start = predicted_ovulation_date - timedelta(days=5)
            fertility_window_end = predicted_ovulation_date + timedelta(days=1)
            return Response({
                'predicted_ovulation_date': predicted_ovulation_date,
                'fertility_window_start': fertility_window_start,
                'fertility_window_end': fertility_window_end
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class PredictionView(APIView):
    permission_classes = [IsAuthenticatedWoman]
    
    def get(self, request):
        try:
            menstruations = request.woman.menstruations.all().order_by('-start_date')
            if menstruations.count()==0:
                return Response({})
            last_period = menstruations.first().start_date
            
            predicted_ovulation_date = last_period + timedelta(days=request.woman.average_cycle_length - 14)
            fertility_window_start = predicted_ovulation_date - timedelta(days=3)
            fertility_window_end = predicted_ovulation_date + timedelta(days=3)
            
            last_menstruation = request.woman.menstruations.order_by('-start_date').first()
            if not last_menstruation:
                return Response({'detail': 'No menstruation data available for prediction'}, status=status.HTTP_404_NOT_FOUND)
            
            predicted_start = last_menstruation.start_date + timedelta(days=request.woman.average_cycle_length)
            predicted_end_date_duration = predicted_start+timedelta(days=int(request.woman.average_menstruation_duration))
            
            today = datetime.now().date()
            if last_menstruation.start_date <= today <= last_menstruation.end_date or predicted_start<=today<=predicted_end_date_duration:
                current_phase = "menstruation"
                advice = random.choice(MENSTRUATION_MESSAGES)
            elif last_menstruation.end_date < today < fertility_window_start:
                current_phase = "normal"
                advice = random.choice(PRE_OVULATION_MESSAGES)
            elif fertility_window_start <= today <= fertility_window_end:
                current_phase = "fertile"
                advice = random.choice(FERTILITY_MESSAGES)
            else:
                current_phase = "normal"
                advice = random.choice(POST_OVULATION_MESSAGES)
            date_range = []
            numdays = 32
            for x in range(-2,numdays):
                if numdays<0:
                    date_x = today - timedelta(days=abs(x))
                else:
                    date_x = today + timedelta(days=x)
                if last_menstruation.start_date <= date_x <= last_menstruation.end_date or predicted_start<=date_x<=predicted_end_date_duration:
                    current_phase = "menstruation"
                    advice = random.choice(MENSTRUATION_MESSAGES)
                elif last_menstruation.end_date < date_x < fertility_window_start:
                    current_phase = "normal"
                    advice = random.choice(PRE_OVULATION_MESSAGES)
                elif fertility_window_start <= date_x <= fertility_window_end:
                    current_phase = "fertile"
                    advice = random.choice(FERTILITY_MESSAGES)
                else:
                    current_phase = "normal"
                    advice = random.choice(POST_OVULATION_MESSAGES)
                date_range.append({'day':date_x.strftime('%Y-%m-%d'), 'status':current_phase})

            data = {
                'current_phase': current_phase,
                'advice': advice,
                'ovulation': {
                    'predicted_ovulation_date': predicted_ovulation_date,
                    'fertility_window_start': fertility_window_start,
                    'fertility_window_end': fertility_window_end
                },
                'menstruation': {
                    'predicted_start_date': predicted_start,
                    'predicted_end_date_duration': predicted_end_date_duration
                },
                'date_range':date_range
            }
            return Response(data,status=200)
        except Exception as e:
            print(traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class WomanLinkSymptomView(APIView):
    permission_classes = [IsAuthenticatedWoman]
    
    def validate(self, data):
        try:
            keys = ['date', 'symptoms']
            today = datetime.today().date()
            date_ = datetime.strptime(data['date'],'%Y-%m-%d').date()
            if any(not Symptom.objects.filter(id_symptom=id_s).exists() for id_s in data['symptoms']):
                return False
            if date_ > today:
                return False
            return True
        except Exception:
            return False
    
    def post(self, request):
        try:
            # request.data.keys() = ['date', 'symptoms']
            woman = request.woman
            woman_symptoms = [ws.id_symptom for ws in woman.symptoms.all()]
            if not self.validate(request.data):
                return Response({'erreur':'Veuillez verifier vos données'},status=400)
            date_symptom = datetime.strptime(request.data['date'], '%Y-%m-%d').date()
            symptom_link_data = request.data
            symptom_link_data['woman'] = woman.id_woman
            symptom_link_serializer = SymptomLinkWomanSerializer(data=symptom_link_data)
            symptom_link_serializer.is_valid(raise_exception=True)
            symptom_link_saved = symptom_link_serializer.save(woman=woman)
            print('symptom link save ....')
            change_ovulation = len(request.data['symptoms']) > 1 and all(
                id_s in woman_symptoms for id_s in request.data['symptoms']
            )
            print(change_ovulation)
            if change_ovulation:
                print('Modification de l\'ovulation...')
                last_period = request.woman.menstruations.order_by('-start_date').first().start_date
                if not last_period:
                    return Response({'detail': 'La date de la dernière période n\'est pas disponible'}, status=status.HTTP_404_NOT_FOUND)
                
                predicted_ovulation_date = last_period + timedelta(days=request.woman.average_cycle_length - 14)
                fertility_window_start = predicted_ovulation_date - timedelta(days=5)
                fertility_window_end = predicted_ovulation_date + timedelta(days=1)
                
                if date_symptom > last_period and fertility_window_end <= date_symptom <= fertility_window_start:
                    last_ovulation = woman.ovulations.order_by("predicted_ovulation_date").last()
                    if last_period > last_ovulation.predicted_ovulation_date:
                        last_ovulation.predicted_ovulation_date = predicted_ovulation_date
                        last_ovulation.fertility_window_start = fertility_window_start
                        last_ovulation.fertility_window_end = fertility_window_end
                        last_ovulation.save()
                        message_notification = get_notification(woman)
                    else:
                        Ovulation.objects.create(
                            woman=woman,
                            predicted_ovulation_date=predicted_ovulation_date,
                            fertility_window_start=fertility_window_start,
                            fertility_window_end=fertility_window_end
                        )
                        message_notification = get_notification(woman)
                    
                    Notification.objects.create(
                        woman=woman,
                        message=message_notification
                    )
                    send_sms(woman.user.phone_number, message_notification)
            
            for id_symptom in request.data['symptoms']:
                symptom = Symptom.objects.get(id_symptom=id_symptom)
                symptom_link_saved.symptoms.add(symptom)
            
            return Response({'message': 'Les symptômes ont été soumis avec succès.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
      
class WomanSymptomsNewView(APIView):
    permission_classes = [IsAuthenticatedWoman]
    
    def validate_data(self, data):
        try:
            keys = ['date', 'description','title']
            if any(key not in data.keys()for key in keys):
                return False
            if 'category'in data:
                if data['category'] not in ['physique','emotion','humeur']:
                    return False
            if 'symptom_type'in data:
                if data['symptom_type']not in ['general','ovulation','menstrual']:
                    return False
            return True
        except Exception:
            return False

    def post(self, request):
        try:
            # request.data = ['date', 'description','title','category', 'symptom_type']
            if not self.validate_data(request.data):
                return Response({'erreur':'Tous les champs sont requis'}, status=status.HTTP_400_BAD_REQUEST)
            symptom_data = request.data
            woman = request.woman
            symptom_data['date'] = datetime.strptime(request.data['date'], "%Y-%m-%d").date()
            serializer = SymptomSerializer(data=symptom_data, context=symptom_data)
            if serializer.is_valid():
                serializer_saved = serializer.save()
                symptom = Symptom.objects.get(id_symptom=serializer_saved.id_symptom)
                woman.symptoms.add(symptom)
                woman.save()
                if woman.ovulations.all().count()>0:
                    ovulation_last = woman.ovulations.order_by("predicted_ovulation_date").last()
                    ovulation_last.symptoms.add(symptom)
                    ovulation_last.save()
                
                return Response({'message':'symptom soumis avec succès'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class WomanSymptomListView(APIView):
    permission_classes = [IsAuthenticatedWoman]

    def get(self, request):
        try:
            data = {
                "physiques":SymptomSerializer(Symptom.objects.filter(category='physique'), many=True, context={'exclude_category':True}).data,
                "emotions":SymptomSerializer(Symptom.objects.filter(category='emotion'), many=True, context={'exclude_category':True}).data
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class WomanSymptomFilterView(APIView):
    permission_classes = [IsAuthenticatedWoman]

    def get(self, request, category):
        try:
            symptoms = Symptom.objects.filter(woman=request.woman,category=category)
            serializer = SymptomSerializer(symptoms, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class MenstruationNewFull(APIView):
    permission_classes = [IsAuthenticatedWoman]
    
    def validate(self, data):
        try:
            keys=['start_date', 'menstruation_duration', 'symptoms','regle_type']
            if any(key not in data.keys()for key in keys):
                return False
            start_date = datetime.strptime(data['start_date'],'%Y-%m-%d')
            if start_date>datetime.now():
                return False
            symptoms = data['symptoms']
            for symptom_id in symptoms:
                if not Symptom.objects.filter(id_symptom=symptom_id).exists():
                    return False
            return True
        except Exception:
            return False

    # request.data.keys = ['start_date', 'cycle_duration', 'menstruation_duration','regle_type', 'symptoms']
    def post(self, request):
        try:
            print(request.data)
            if not self.validate(request.data):
                return Response({'error':'veuillez verifier votre donné'},status=400)
            woman = request.woman
            start_date = datetime.strptime(request.data['start_date'], '%Y-%m-%d').date()
            if woman.menstruations.all().count()!=0:
                last_menstruation = woman.menstruations.all().order_by('-start_date').first()

            woman.update_average_menstruation_length()

            duration = request.data.get('menstruation_duration',woman.average_menstruation_duration)
            end_date = start_date +timedelta(days=int(duration)) if duration is not None else start_date + timedelta(days=woman.average_menstruation_duration)
            data = {
                'start_date': start_date,
                'end_date': end_date,
                'woman':woman
                }

            serializer = MenstruationSerializer(data=data)
            if serializer.is_valid():
                if 'cycle_duration' in request.data:
                    menstruation = serializer.save(woman=woman)
                    today_date = datetime.today().date()
                    next_start_date = start_date+timedelta(int(request.data['cycle_duration']))
                    next_end_date = next_start_date + timedelta(days=woman.average_menstruation_duration)
                    print(today_date, next_start_date, today_date >= next_start_date)
                    if today_date >= next_start_date:
                        Menstruation.objects.create(start_date=next_start_date,end_date=next_end_date,woman=woman)
                else:
                    menstruation= serializer.save()
                last_menstruation = woman.menstruations.all().order_by('-start_date').first()
                woman.last_period_date = last_menstruation.start_date
                
                woman.update_average_menstruation_length()
                woman.update_average_cycle_length()
                woman.save()
                
                predicted_ovulation_date = last_menstruation.start_date + timedelta(days=woman.get_cycle() - 14)
                fertility_window_start = predicted_ovulation_date - timedelta(days=4)
                fertility_window_end = predicted_ovulation_date + timedelta(days=3)
                
                Ovulation.objects.create(
                    woman=woman,
                    predicted_ovulation_date=predicted_ovulation_date,
                    fertility_window_start=fertility_window_start,
                    fertility_window_end=fertility_window_end
                )
                for symptom_id in request.data['symptoms']:
                    symptom = Symptom.objects.get(id_symptom=int(symptom_id))
                    woman = request.woman
                    woman.symptoms.add(symptom)
                    woman.save()
                
                notification_message = get_notification(woman)
                Notification.objects.create(
                    woman=woman,
                    message=notification_message
                )
                send_sms(woman.user.phone_number, notification_message)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            print('serializer is not valid...')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)