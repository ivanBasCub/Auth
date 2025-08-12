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

    return render(request, "dashboard.html",{
        "main_pj" : main_pj,
        "list_alts" : list_alts,
        "groups" : request.user.groups.all()
    })

@login_required(login_url='/')
def audit_account(request):
    list_pjs = EveCharater.objects.filter(user_character = request.user).all()

    main_pj = list_pjs.filter(main=True).first()
    list_alts = list_pjs.filter(main=False).all()

    return render(request, "audit.html",{
        "main_pj" : main_pj,
        "list_pjs" : list_pjs
    })