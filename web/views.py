from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sso.models import EveCharater
import esi.views as esi_views
# Create your views here.
def index(request):
    return render(request, "index.html")

@login_required(login_url='/')
def dashboard(request):
    main_pj = EveCharater.objects.filter(main=True, user_character = request.user).first()
    list_alts = EveCharater.objects.filter(main=False, user_character = request.user).all()

    for alt in list_alts:
        alt = esi_views.character_corp_alliance_info(alt)

    return render(request, "dashboard.html",{
        "main_pj" : main_pj,
        "list_alts" : list_alts,
        "groups" : request.user.groups.all()
    })

@login_required(login_url='/')
def audit_account(request):
    list_pjs = EveCharater.objects.filter(user_character = request.user).all()

    for pj in list_pjs:
        pj = esi_views.character_corp_alliance_info(pj)
        pj = esi_views.character_wallet_money(pj)

    main_pj = list_pjs.filter(main=True).first()
    list_alts = list_pjs.filter(main=False).all()

    return render(request, "audit.html",{
        "main_pj" : main_pj,
        "list_pjs" : list_pjs
    })