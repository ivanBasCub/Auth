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
        alt = esi_views.character_extra_info(alt)

    return render(request, "dashboard.html",{
        "main_pj" : main_pj,
        "list_alts" : list_alts
    })