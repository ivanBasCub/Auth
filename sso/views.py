from django.shortcuts import redirect
from django.conf import settings
import random
import string
import urllib.parse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from .models import EveCharater
from base64 import b64encode
import requests
from datetime import datetime, timedelta
import esi.views as esi_views

# Funcion para llamar hacer el login con la web de Eve
def eve_login(request):
    state = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    params = {
        'response_type': 'code',
        'client_id': settings.CLIENT_ID,
        'redirect_uri': settings.CALLBACK_URL,
        'scope': settings.EVE_SCOPE,
        'state': state
    }

    url = 'https://login.eveonline.com/v2/oauth/authorize?' + urllib.parse.urlencode(params)
    return redirect(url)

# Funcion de autenticación del login con eve y creacion de los tokens y obtener la información principal del personaje
def eve_callback(request):
    code = request.GET.get('code')

    headers = {
        'Authorization' : f'Basic {b64encode(f"{settings.CLIENT_ID}:{settings.CLIENT_SECRET}".encode()).decode()}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.CALLBACK_URL,
    }
    # Funciona
    response = requests.post('https://login.eveonline.com/v2/oauth/token', headers=headers, data=data)
    tokens = response.json()

    url = 'https://login.eveonline.com/oauth/verify'
    header = {
        'Authorization': f'Bearer {tokens["access_token"]}'
    }

    res = requests.get(url, headers=header)
    user_info = res.json()

    return check_account(request, tokens, user_info)

# Funciones para comprobar las cuentas
def check_account(request, tokens, user_info):
    if request.user.is_authenticated:
        return register_eve_character(request, tokens, user_info)
    else:
        return update_create_user(request, tokens, user_info)

# Caso de que haya una cuenta logeada
def register_eve_character(request, tokens, user_info):
    check = EveCharater.objects.filter(characterName = user_info["CharacterName"])
    actual_hour = datetime.now().time()
    complete_hour = datetime.combine(datetime.today(), actual_hour)
    expiration = (complete_hour + timedelta(minutes=20)).time()

    if check.exists():
        refresh_eve_character(user_info, tokens, expiration)

        return redirect("../../auth/dashboard/")
    else:
        save_eve_character(request.user, user_info, tokens, expiration)

        return redirect("../../auth/dashboard/")

# Caso de que no haya una cuenta logeada
def update_create_user(request, tokens, user_info):
    actual_hour = datetime.now().time()
    complete_hour = datetime.combine(datetime.today(), actual_hour)
    expiration = (complete_hour + timedelta(minutes=20)).time()

    try:
        # Caso de que el usuario y el pj existan en la BBDD
        user = User.objects.get(username = user_info["CharacterName"])
        refresh_eve_character(user_info, tokens, expiration)

        login(request,user)

    except User.DoesNotExist:
        check = EveCharater.objects.filter(characterName = user_info["CharacterName"])

        if check.exists():
            return redirect("../../")
        
        user = User.objects.create(username = user_info["CharacterName"])
        user.save()

        save_eve_character(user, user_info, tokens, expiration)

        login(request, user)

    return redirect("../../auth/dashboard/")

# Funcion para guardar el personaje
def save_eve_character(user, user_info, tokens, expiration):

    character = EveCharater.objects.create(
            characterId = user_info["CharacterID"],
            characterName = user_info["CharacterName"],
            accessToken = tokens["access_token"],
            refreshToken = tokens["refresh_token"],
            expiration = expiration,
            main = False,
            user_character = user
        )
    if user.username == user_info["CharacterName"]:
        character.main = True

    character = esi_views.character_corp_alliance_info(character)
    character = esi_views.character_wallet_money(character)
    character = esi_views.character_skill_points(character)
        
    character.save()

# Funcion para actualizar la información del personaje
def refresh_eve_character(user_info, tokens, expiration):
    character = EveCharater.objects.get(characterName = user_info["CharacterName"])
    character.accessToken = tokens["access_token"]
    character.refreshToken = tokens["refresh_token"]
    character.expiration = expiration
    character = esi_views.character_corp_alliance_info(character)
    character = esi_views.character_wallet_money(character)
    character = esi_views.character_skill_points(character)
        
    character.save()

# Funcion para refrescar el token de los pj de Eve
def refresh_token(character):

    headers = {
        'Authorization' : f'Basic {b64encode(f"{settings.CLIENT_ID}:{settings.CLIENT_SECRET}".encode()).decode()}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
        'grant_type' : 'refresh_token',
        'refresh_token' : character.refreshToken
    }

    response = requests.post(
        url= settings.EVE_REFRESH_TOKEN_URL,
        headers=headers,
        data= data
    )

    if response.status_code == 200:
        tokens = response.json()
        actual_hour = datetime.now().time()
        complete_hour = datetime.combine(datetime.today(), actual_hour)
        expiration = (complete_hour + timedelta(minutes=20)).time()

        character.accessToken = tokens['access_token']
        character.refreshToken = tokens["refresh_token"]
        character.expiration = expiration
        character = esi_views.character_corp_alliance_info(character)
        character = esi_views.character_wallet_money(character)
        character = esi_views.character_skill_points(character)
        character.save()

    else:
        print(f"Error al refrescar token de {character.characterName}: {response.text}")

    return redirect("auth/dashboard/")


def eve_logout(request):
    logout(request)
    return redirect("/")