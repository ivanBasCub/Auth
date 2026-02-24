from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .utils import create_fats
from sso.models import Eve_Character
from doctrines.models import Doctrine
from .models import Fleet, FleetType, Fat_Character, SRP, SRP_Ship
from .utils import create_srp_request
from utils.views import format_number

# Views Fleet Feature

## USER VIEWS

### List of fats
@login_required(login_url="/")
def fat_list(request):
    limit_30_days = timezone.now() - timedelta(days=30)

    list_pj = Eve_Character.objects.filter(user = request.user).all()
    main_pj = list_pj.filter(main=True).first()
    fats = Fleet.objects.filter(date__gte = limit_30_days).order_by('date').all()
    fat_list = Fat_Character.objects.filter(fleet__in = fats, character__in = list_pj).all()

    return render(request, "fat/list.html",{
        "main_pj" : main_pj,
        "list_pj" : list_pj,
        "fats" : fat_list
    })

### Create new fleet
@login_required(login_url="/")
def add_fat(request):
    list_pj = Eve_Character.objects.filter(user = request.user).all()
    main_pj = list_pj.filter(main=True).first()
    doctrines = Doctrine.objects.all()
    fleet_types = FleetType.objects.all()

    if request.method == "POST":
        pj_id = int(request.POST.get("fc",0).strip())
        doctrine_id = int(request.POST.get("doctrine",0).strip())
        fleet_type_id = int(request.POST.get("type",0).strip())
        fleet_name = request.POST.get("name","").strip()

        if pj_id != 0 and doctrine_id != 0 and fleet_type_id != 0 and fleet_name != "":
            try:
                create_fats(pj_id, doctrine_id, fleet_type_id, fleet_name)
            except Exception as e:
                print("Error creating fats:", e)

        return redirect("/auth/fats/list/")
    else:
        return render(request, "fat/add.html",{
            "main_pj" : main_pj,
            "list_pj" : list_pj,
            "fleet_types" : fleet_types,
            "doctrines" : doctrines
        })

# Views to SRP System

## USER VIEW

### Index SRP
@login_required(login_url="/")
def srp_index(request):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)
    list_srp = SRP.objects.all()
    total_cost = 0
    for srp in list_srp:
        total_cost += srp.srp_cost
        srp.srp_cost = format_number(srp.srp_cost)
        srp.pending_requests = SRP_Ship.objects.filter(srp = srp, status = 0).count()

    total_cost = format_number(total_cost)

    return render(request,"srp/index.html",{
        "main_pj" : main_pj,
        "total_cost" : total_cost,
        "list_srp": list_srp
    })

### Request SRP
@login_required(login_url="/")
def srp_request(request, srp_id):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)
    srp = SRP.objects.get(srp_id = srp_id)
    
    if request.method == "POST":
        zkill_link = request.POST.get("zkill","").strip()
        if zkill_link != "":
            zkill_id = zkill_link.strip("/").split("/")[-1]
            create_srp_request(zkill_id, srp)

            return redirect(f"/auth/fats/srp/{srp_id}/view/")

    return render(request,"srp/request.html",{
        "main_pj" : main_pj,
        "srp" : srp
    })
    
### View SRP
@login_required(login_url="/")
def srp_view(request, srp_id):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)
    srp = SRP.objects.get(srp_id = srp_id)
    list_srp_ships = SRP_Ship.objects.filter(srp = srp).all()
    lost_count = list_srp_ships.count()
    
    srp.srp_cost = format_number(srp.srp_cost)
    return render(request,"srp/view.html",{
        "main_pj" : main_pj,
        "list_srp_ships" : list_srp_ships,
        "lost_count" : lost_count,
        "srp" : srp
    })
    
### Admin SRP
@login_required(login_url="/")
def srp_admin(request, srp_id):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)

    if request.method == "POST":
        status = 0
        srp_request_id = 0
        srp_status = 0

        if "status" in request.POST:
            status = int(request.POST.get("status",0).strip())
            srp_request_id = int(request.POST.get("srp_request",0).strip())
        elif "srp_status" in request.POST:
            srp_status = int(request.POST.get("srp_status",0).strip())
        
        if srp_request_id != 0:
            srp_request = SRP_Ship.objects.get(id = srp_request_id)
            srp_request.status = status
            srp_request.save()

        if srp_status != 0:
            srp = SRP.objects.get(srp_id = srp_id)
            srp.status = srp_status
            srp.save()

            return redirect("/auth/fats/srp/")

    srp = SRP.objects.get(srp_id = srp_id)
    list_srp_ships = SRP_Ship.objects.filter(srp = srp, status = 0).all()
    check_srp_list = SRP_Ship.objects.filter(srp = srp).exclude(status = 0).all()

    return render(request,"srp/admin.html",{
        "main_pj" : main_pj,
        "list_srp_ships" : list_srp_ships,
        "check_srp_list" : check_srp_list
    })