from dotenv import load_dotenv
from datetime import timedelta
from django.utils import timezone as django_timezone

from apps.users.models import SmsOrangeToken
from apps.menstruation.models import Woman, Notification

import http.client
import base64
import urllib.parse
import os
import requests
import pyttsx3
import datetime
import random
import json

load_dotenv()

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
    
    encouragement_messages = [
        "Courage pendant cette période, prenez soin de vous ! 💪",
        "N'oubliez pas de bien vous hydrater et de vous reposer. 🌸",
        "Vous êtes forte ! Prenez le temps de vous détendre. 🌼",
        "Prenez du temps pour vous, c'est essentiel ! 💖",
    ]

    for woman in Woman.objects.all():
        if woman.last_period_date:
            cycle_length = woman.average_cycle_length or 28
            menstruation_duration = woman.average_menstruation_duration or 5
            next_period_start = woman.last_period_date + datetime.timedelta(days=cycle_length)
            period_end = woman.last_period_date + datetime.timedelta(days=menstruation_duration)
            ovulation_day = woman.last_period_date + datetime.timedelta(days=cycle_length - 14) 
            fertility_start = ovulation_day - datetime.timedelta(days=5)
            fertility_end = ovulation_day + datetime.timedelta(days=5)

            if next_period_start - now == datetime.timedelta(days=1):
                message = "Votre cycle va bientôt commencer. Pensez à préparer ce dont vous avez besoin. 🌸"
                send_sms(woman.user.phone, message)
                Notification.objects.create(woman=woman, message=message)

            if now == next_period_start:
                message = "Vos règles viennent de commencer. Prenez soin de vous pendant cette période. 💖"
                send_sms(woman.user.phone, message)
                Notification.objects.create(woman=woman, message=message)

            if woman.last_period_date <= now <= period_end:
                if random.choice([True, False]):
                    message = random.choice(encouragement_messages)
                    send_sms(woman.user.phone, message)
                    Notification.objects.create(woman=woman, message=message)

            if now == period_end:
                message = "Votre période menstruelle se termine aujourd'hui. Prenez soin de vous ! 🌷"
                send_sms(woman.user.phone, message)
                Notification.objects.create(woman=woman, message=message)

            if fertility_start <= now <= fertility_end:
                if now == fertility_start:
                    message = "Votre période de fertilité commence aujourd'hui. Soyez attentive à votre santé. 🌸"
                elif now == ovulation_day:
                    message = "Aujourd'hui est votre jour d'ovulation. Prenez soin de vous et soyez prudente. 🌼"
                elif now == fertility_end:
                    message = "Votre fenêtre de fertilité se termine aujourd'hui. Continuez de prendre soin de vous. 🌹"
                else:
                    message = "Vous êtes actuellement dans votre période de fertilité. Restez vigilante et prenez soin de vous. 🌼"
                
                send_sms(woman.user.phone_number, message)
                Notification.objects.create(woman=woman, message=message)
