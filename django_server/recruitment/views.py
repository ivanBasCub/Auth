from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sso.models import EveCharater
from .models import Applications_access
from utils.views import format_number
from django.contrib.auth.models import User, Group

# USER VIEW

## Old user create request
@login_required(login_url="/")
def applications_request(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)

    if request.method == "POST":
        msg = request.POST.get("msg",0).strip()
        try:
            application = Applications_access.objects.create(
                user = request.user,
                msg = msg,
                application_type = 2
            )
            application.save()

            return render(request, "recruitment/applications/request.html",{
                "main_pj" : main_pj,
                "mostrar_modal" : True,
                "modal_status" : 1
            })
        except Exception as e:
            return render(request, "recruitment/applications/request.html",{
                "main_pj" : main_pj,
                "mostrar_modal" : True,
                "modal_status" : 2,
                "code_error": type(e).__name__,
            })

    return render(request, "recruitment/applications/request.html",{
        "main_pj" : main_pj,
    })

# ADMIN VIEW

# View Access Applications
@login_required(login_url="/")
def applications_list(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    list_applications = Applications_access.objects.all()
    for application in list_applications:
        application.totalSP = format_number(application.totalSP)

    return render(request, "recruitment/applications/index.html",{
        "main_pj" : main_pj,
        "applications": list_applications
    })

## View list of ex-members
@login_required(login_url="/")
def frigde(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    list_mains = User.objects.filter(groups__name = "Miembro").all()
    list_mains = list_mains.exclude(username = "Adjutora_Helgast").all()

    if request.method == "POST":
        user_id = int(request.POST.get("user_id",0).strip())

        if user_id != 0:
            user = User.objects.get(id=user_id)
            user.groups.clear()
            ice_group = Group.objects.get(name = "Reserva Imperial")
            user.groups.add(ice_group)
            user.save()

    return render(request, "recruitment/fridge/index.html",{
        "main_pj" : main_pj,
        "list_main" : list_mains
    })