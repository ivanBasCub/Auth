from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from sso.models import EveCharater
from ban.models import BannedCharacter
from recruitment.models import Applications_access
from skillplans.models import Skillplan, Skillplan_CheckList
from django.contrib.auth.models import User, Group
from fats.models import Fats_Character
from utils.views import format_number, create_csv
from django.utils import timezone
from datetime import timedelta

# Admin view

# Admin user control
@login_required(login_url="/")
def user_control_list(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    
    if request.method == "POST":
        user_id = int(request.POST.get("id",0).strip())

        user = User.objects.get(id = user_id)
        list_pjs = EveCharater.objects.filter(user_character = user).all()

        if user:
            for pj in list_pjs:
                pj.main = False
                pj.user_character = User.objects.get(username = "Adjutora_Helgast")
                pj.deleted = True
                pj.save()
            
            Applications_access.objects.filter(user = user).delete()
            user.delete()


    list_mains = User.objects.exclude(username__in = ["Adjutora_Helgast","admin","root"]).all()
    for main in list_mains:
        main.username = main.username.replace("_"," ")

    return render(request, "corp/user/index.html",{
        "main_pj": main_pj,
        "list_main": list_mains
    })

# Reports

# Member Report
@login_required(login_url="/")
def report_members_list(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    members = EveCharater.objects.filter(main= True).all()
    
    for member in members:
        user = User.objects.prefetch_related('groups').get(username = member.characterName.replace(' ','_'))
        member.groups = user.groups.all()
        member.alts_list = EveCharater.objects.filter(user_character = user, main = False).all()
        for alt in member.alts_list:
            member.walletMoney += alt.walletMoney
        member.ban = BannedCharacter.objects.filter(character_id = member.characterId).exists()

    if request.method == "POST":
        if "csv" in request.POST:
            file_name = "memberlist" + str(timezone.now().strftime("%Y%m%d%H%M%S")) + ".csv"
            list_data = [["Main","Groups","Lista Negra","Alts", "Skill Points", "Total ISK"]]
            for member in members:
                list_data.append([
                        member.characterName,
                        member.groups, 
                        member.ban,
                        "/ ".join(map(lambda alt: alt.characterName, member.alts_list)),
                        member.totalSkillPoints,
                        member.walletMoney     
                ])
                        
            create_csv(list_data, file_name)

            return redirect(f"/static/csv/{file_name}")

    for member in members: 
        member.walletMoney = format_number(member.walletMoney)
        member.totalSkillPoints = format_number(member.totalSkillPoints)

    return render(request, "corp/reports/members.html",{
        "main_pj" : main_pj,
        "members" : members
    })
    
# Fats Report
@login_required(login_url="/")
def fats_reports(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    user_list = User.objects.exclude(username__in=["Adjutora Helgast","admin","root"]).all()
    three_months = timezone.now() - timedelta(days=90)
    fats = Fats_Character.objects.filter(fat__date__gte = three_months).all()

    for user in user_list:
        user_fats = fats.filter(character__user_character = user).all()
        user.totalFats = user_fats.count()
        user.cta = user_fats.filter(fat__fleetType__name = "CTA").count()
        user.stratop = user_fats.filter(fat__fleetType__name = "Strat-Op").count()
        user.hd = user_fats.filter(fat__fleetType__name = "Home Defense").count()
        user.roam = user_fats.filter(fat__fleetType__name = "Roam").count()

    if request.method == "POST":
        if "csv" in request.POST:
            file_name = "fats_reports" + str(timezone.now().strftime("%Y%m%d%H%M%S")) + ".csv"
            list_data = [["Main","Total Fats","CTA", "Strat-Op", "Home Defense", "Roam"]]
            for user in user_list:
                list_data.append([
                    user.username,
                    user.totalFats,
                    user.cta,
                    user.stratop,
                    user.hd,
                    user.roam
                ])
                        
            create_csv(list_data, file_name)

            return redirect(f"/static/csv/{file_name}")
    
    return render(request, "corp/reports/fats.html",{
        "main_pj" : main_pj,
        "user_list": user_list
    })

# Skillplan Report
@login_required(login_url="/")
def skillplan_reports(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    skillplans = Skillplan.objects.filter(name__in = ["Guardia Imperial","Vanguardia","Legionario","Primaris","Campeon del capitulo","Ultramarine","DeathWacth","Magic 14"]).all()
    corp_members = User.objects.filter(groups__name = "Miembro")
    main_list = EveCharater.objects.filter(main = True, user_character__in=corp_members).all()
    
    for main in main_list:
        main.skillplanCheck = Skillplan_CheckList.objects.filter(character = main,skillPlan__in = skillplans).all().order_by("skillPlan")
    
    if request.method == "POST":
        if "csv" in request.POST:
            file_name = "skillplan" + str(timezone.now().strftime("%Y%m%d%H%M%S")) + ".csv"
            list_data = [["Main","Guardia Imperial","Vanguardia","Legionario","Primaris","Campeon del capitulo","Ultramarine","DeathWacth","Magic 14"]]
            for main in main_list:
                data = [main.characterName]
                for sp in main.skillplanCheck:
                    data.append(sp.status)
                list_data.append(data)
            create_csv(list_data, file_name)

            return redirect(f"/static/csv/{file_name}")


    return render(request, "corp/reports/skill_plans.html",{
        "main_pj" : main_pj,
        "skillplans" : skillplans,
        "main_list": main_list
    })
    
# Groups Report
@login_required(login_url="/")
def groups_report(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    groups = Group.objects.all().prefetch_related('user_set')
    
    if request.method == "POST":
        if "csv" in request.POST:
            file_name = "groups_report" + str(timezone.now().strftime("%Y%m%d%H%M%S")) + ".csv"
            list_data = [["Group","Number of Mains","List of Mains"]]
            for group in groups:
                mains = [user.username.replace('_',' ') for user in group.user_set.all()]
                list_data.append([
                    group.name,
                    len(mains),
                    "/ ".join(mains)
                ])
                        
            create_csv(list_data, file_name)

            return redirect(f"/static/csv/{file_name}")
    
    return render(request, "corp/reports/groups.html",{
        "main_pj" : main_pj,
        "groups": groups
    })
    
