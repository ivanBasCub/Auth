from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sso.models import EveCharater
import esi.views as esi_views
import sso.views as sso_views
from doctrines.models import Doctrine, FitShip

# Create your views here.
def index(request):
    return render(request, "index.html")

@login_required(login_url='/')
def dashboard(request):
    list_pjs = EveCharater.objects.filter(user_character = request.user).all()

    main_pj = list_pjs.filter(main=True).first()
    list_alts = list_pjs.filter(main=False).all()

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

@login_required(login_url='/')
def fittings(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    doctrines = Doctrine.objects.exclude(doctitle = "X").all()

    return render(request, "fittings.html", {
        "main_pj" : main_pj,
        "list_doctrines" : doctrines
    })

@login_required(login_url="/")
def doctrine(request, doc_id):
    doctrine = Doctrine.objects.get(id = doc_id)
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)

    doctrine_fits = FitShip.objects.filter(fitDoctrine = doctrine).all()

    return render(request, "doctrines.html",{
        "main_pj" : main_pj,
        "doctrine" : doctrine,
        "fits" : doctrine_fits
    })

@login_required(login_url="/")
def fit(request, fit_id):
    fit_data = FitShip.objects.get(id = fit_id)
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    
    item_list = fit_data.items

    hi_items = [item for item in item_list if item.get("flag").startswith("HiSlot")]
    hi_slots = f"img/{len(hi_items)}h.png"
    med_items = [item for item in item_list if item.get("flag").startswith("MedSlot")]
    med_slots = f"img/{len(med_items)}m.png"
    lo_items = [item for item in item_list if item.get("flag").startswith("LoSlot")]
    lo_slots = f"img/{len(lo_items)}l.png"
    rig_items = [item for item in item_list if item.get("flag").startswith("RigSlot")]
    rig_slots = f"img/{len(rig_items)}r.png"
    subsystem_items = [item for item in item_list if item.get("flag").startswith("SubSystemSlot")]
    cargo_items = [item for item in item_list if item.get("flag").startswith("Cargo")]
    drones_items = [item for item in item_list if item.get("flag").startswith("DroneBay")]
    fighters_items = [item for item in item_list if item.get("flag").startswith("FighterBay")]

    return render(request, "fit.html",{
        "main_pj" : main_pj,
        "fit" : fit_data,
        "hi_items" : hi_items,
        "med_items" : med_items,
        "lo_items" : lo_items,
        "rig_items" : rig_items,
        "subsystem_items" : subsystem_items,
        "cargo_items" : cargo_items,
        "drones_items" : drones_items,
        "fighters_items" : fighters_items,
        "hi_slots" : hi_slots,
        "med_slots" : med_slots,
        "lo_slots" : lo_slots,
        "rig_slots" : rig_slots,
    })