from django.shortcuts import redirect, render
from django.conf import settings
import random
import string
import urllib.parse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User, Group
from .models import EveCharater
from base64 import b64encode
import requests
from datetime import timedelta
from django.utils import timezone
import esi.views as esi_views
import ban.models as ban_models
from recruitment.models import Applications_access
import secrets

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
    
    # Comprobar si el personaje esta baneado
    if ban_models.BannedCharacter.objects.filter(character_id=user_info["CharacterID"]).exists():
        return ban_notice(request)

    if request.user.is_authenticated:
        return register_eve_character(request, tokens, user_info)
    else:
        return update_create_user(request, tokens, user_info)

# Caso de que haya una cuenta logeada
def register_eve_character(request, tokens, user_info):
    check = EveCharater.objects.filter(characterName = user_info["CharacterName"])
    expiration = timezone.now() + timedelta(minutes=20)

    if check.exists():
        refresh_eve_character(user_info, tokens, expiration)

        return redirect("../../auth/dashboard/")
    else:
        save_eve_character(request.user, user_info, tokens, expiration)

        return redirect("../../auth/dashboard/")

# Caso de que no haya una cuenta logeada
def update_create_user(request, tokens, user_info):
    expiration = timezone.now() + timedelta(minutes=20)
    characters = string.ascii_letters + string.digits + string.punctuation
    random_password = ''.join(secrets.choice(characters) for i in range(16))

    try:
        # Caso de que el usuario y el pj existan en la BBDD
        user = User.objects.get(username = user_info["CharacterName"].replace(" ","_"))
        user.set_password(random_password)
        user.save()
        refresh_eve_character(user_info, tokens, expiration)

        login(request,user)

    except User.DoesNotExist:
        check = EveCharater.objects.filter(characterName = user_info["CharacterName"])

        if check.exists():
            return redirect("../../")
        
        member_group = Group.objects.get_or_create(name = "Miembro")
        user = User.objects.create(username = user_info["CharacterName"].replace(" ","_"))
        user.set_password(random_password)
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
    
    character = esi_views.character_corp_alliance_info(character)
    
    if character.corpId == 98628176:
        member_group = Group.objects.get(name = "Miembro")
        user.groups.add(member_group)
        user.save()

    character = esi_views.character_wallet_money(character)

    if user.username == user_info["CharacterName"].replace(" ","_"):
        character.main = True

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

# Funcion de aviso de ban
def ban_notice(request):
    return render(request, "index.html", {"mostrar_modal": True})


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
        expiration = timezone.now() + timedelta(minutes=20)

        character.accessToken = tokens['access_token']
        character.refreshToken = tokens["refresh_token"]
        character.expiration = expiration
        character = esi_views.character_corp_alliance_info(character)
        character = esi_views.character_wallet_money(character)
        character = esi_views.character_skill_points(character)
        user = character.user_character

        if character.main == True and character.corpId != 98628176:
            if user.groups.filter(name="Reserva Imperial").exists():
                user.groups.clear()
                ice_group = Group.objects.get(name = "Reserva Imperial")
                user.groups.add(ice_group)
            else:
                user.groups.clear()
        
        if character.main == True and character.corpId == 98628176:
            group_member = Group.objects.get(name="Miembro")
            user.groups.add(group_member)

        user.save()
        character.save()

        application = Applications_access.filter(user = user).delete()

    else:
        print(f"Error al refrescar token de {character.characterName}: {response.text}")


def eve_logout(request):
    logout(request)
    return redirect("/")

def inactive_user():
    limit_time = timezone.now() - timedelta(days=30)
    inactive_group = Group.objects.get_or_create(name="Reserva Imperial")
    list_members = User.objects.filter(last_login__lt=limit_time)

    for member in list_members:
        member.groups.clear()
        member.groups.add(inactive_group)
        member.save()