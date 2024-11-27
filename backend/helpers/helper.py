from dotenv import load_dotenv
from datetime import timedelta, datetime
from django.utils import timezone as django_timezone

from apps.users.models import SmsOrangeToken
from apps.menstruation.models import Woman, Notification

import http.client
import base64
import urllib.parse
import os
import requests
import pyttsx3
import random
import json

load_dotenv()


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
    menstruations = woman.menstruations.order_by('-start_date')
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
    if today.strftime('%Y-%m-%d')in [(m.start_date-timedelta(days=2)).strftime('%Y-%m-%d') for m in woman.menstruations.order_by('start_date')]+[(predicted_start-timedelta(days=2)).strftime('%Y-%m-%d')]:
        current_phase = "normal"
        advice = random.choice(PRE_MENSTRUATION_TWO_DAYS)
    elif today.strftime('%Y-%m-%d')in [(m.start_date-timedelta(days=1)).strftime('%Y-%m-%d') for m in woman.menstruations.order_by('start_date')]+[(predicted_start-timedelta(days=1)).strftime('%Y-%m-%d')]:
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

def get_timezone():
    tz = os.getenv("TIMEZONE_HOURS")
    if '-' in tz:
        return django_timezone.now() - timedelta(hours=int(tz.strip()[1:]))
    return django_timezone.now()+timedelta(hours=int(tz))

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    
def helloworld():
    RASA = os.getenv('RASA')
    response = requests.request("GET", RASA)
    return response.text

def messageChatRASA(message, sender="Anonymous", debug=0):
    RASA_API = os.getenv('RASA_URL')
    
    data = {
        "sender": sender,
        "message": str(message)
    }

    headers = {
        'Content-Type': "application/json",
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
    }

    try:
        response = requests.post(RASA_API, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Unexpected response", "status_code": response.status_code}
    except Exception as e:
        return {"error": "ERROR 1", "details": str(e)}

def getAuthToken():
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')

    authString = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode('utf-8')

    params = urllib.parse.urlencode({
        "grant_type": "client_credentials"
    })

    headersMap = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + authString
    }

    conn = http.client.HTTPSConnection("api.orange.com")
    conn.request("POST", "/oauth/v3/token", body=params, headers=headersMap)

    response = conn.getresponse()
    
    if response.status == 200:
        data = response.read()
        result = json.loads(data)
        sms_tokens = SmsOrangeToken.objects.all()
        if len(sms_tokens)>0:
            sms_token_last = sms_tokens.last()
            sms_token_last.token_access = result.get('access_token')
            sms_token_last.token_type = result.get('token_type')
            sms_token_last.token_validity = result.get('expires_in')
            sms_token_last.save()
        else:
            SmsOrangeToken.objects.create(token_access=result.get('access_token'), token_type=result.get('token_type'),token_validity=result.get('expires_in'))
        return result
    else:
        print("Error:", response.status, response.reason)
        data = response.read()
        print("Response:", data)
    conn.close()
    return None

def getOrangeToken():
    sms_tokens = SmsOrangeToken.objects.all()
    if len(sms_tokens)==0:
        return getAuthToken().get('access_token')
    return sms_tokens.last().token_access

def send_sms(recipient_phone, message):
    print(f'sending message : {message}  To {recipient_phone}')
    dev_phone = os.getenv('DEV_PHONE_NUMBER')
    token = getAuthToken().get('access_token')

    url = f"/smsmessaging/v1/outbound/tel%3A%2B{dev_phone}/requests"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    body = json.dumps({
        "outboundSMSMessageRequest": {
            "address": f"tel:{recipient_phone}",
            "senderAddress": f"tel:+{dev_phone}",
            "outboundSMSTextMessage": {
                "message": message
            }
        }
    })

    conn = http.client.HTTPSConnection("api.orange.com")
    conn.request("POST", url, body=body, headers=headers)

    response = conn.getresponse()
    data = response.read()
    conn.close()
    print(json.loads(data), response.reason, response.status)
    return json.loads(data) if response.status == 201 else {"error": response.status, "message": response.reason}

def sms_balance():
    token = token = getOrangeToken()
    url = f"/sms/admin/v1/contracts"

    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    conn = http.client.HTTPSConnection("api.orange.com")
    print('before posting....')
    conn.request("GET", url, headers=headers)

    response = conn.getresponse()
    data = response.read()
    conn.close()

    return json.loads(data) if response.status == 200 else {"error": response.status, "message": response.reason}

def sms_usage():
    token = token = getOrangeToken()

    url = f"/sms/admin/v1/statistics"

    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    conn = http.client.HTTPSConnection("api.orange.com")
    print('before posting....')
    conn.request("GET", url, headers=headers)

    response = conn.getresponse()
    data = response.read()
    conn.close()

    return json.loads(data) if response.status == 200 else {"error": response.status, "message": response.reason}

def sms_purchase_history():
    token = token = getOrangeToken()

    url = f"/sms/admin/v1/purchaseorders"

    headers = {
        "Content-Type":"application/json",
        "Authorization": f"Bearer {token}"
    }
    
    conn = http.client.HTTPSConnection("api.orange.com")
    conn.request("GET", url, headers=headers)

    response = conn.getresponse()
    data = response.read()
    conn.close()

    return json.loads(data) if response.status == 200 else {"error": response.status, "message": response.reason}


def check_and_notify_women():
    now = django_timezone.now().date()

    for woman in Woman.objects.all():
        message_notification = get_notification(woman)
        send_sms(woman.user.phone_number, message_notification)
        Notification.objects.create(woman=woman, message=message_notification)
