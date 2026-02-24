from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from sso.models import EveCharater
from skillplans.models import Skillplan, Skillplan_CheckList
from recruitment.models import Applications_access
from utils.views import format_number, check_skill

# INDEX
def index(request):
    if request.user.is_authenticated:
        return redirect("/auth/dashboard/")
    else:
        return render(request, "index.html")

# AUTH

## DASHBOARD
@login_required(login_url='/')
def dashboard(request):
    list_pjs = EveCharater.objects.filter(user_character = request.user).all()

    main_pj = list_pjs.filter(main=True).first()
    list_alts = list_pjs.filter(main=False).all()

    application = Applications_access.objects.filter(user = request.user).first()

    if application:
        disable_btn = True
    else:
        disable_btn = False

    return render(request, "dashboard.html",{
        "main_pj" : main_pj,
        "list_alts" : list_alts,
        "groups" : request.user.groups.all(),
        "disable_btn" : disable_btn
    })

## CHANGE MAIN
@login_required(login_url='/')
def change_main(request):
    
    if request.method == "POST":
        token_id = int(request.POST.get("token",0))

        if token_id != 0:
            new_main = EveCharater.objects.get(id = token_id)
            main_pj = EveCharater.objects.filter(user_character = request.user, main = True).first()
            main_pj.main = False
            main_pj.save()
            new_main.main = True
            new_main.save()

            request.user.username = new_main.characterName.replace(" ","_")
            request.user.save()

            return redirect("/auth/dashboard")

    list_pjs = EveCharater.objects.filter(user_character = request.user).all()
    main_pj = list_pjs.filter(main=True).first()

    return render(request, "audit/main.html",{
        "main_pj": main_pj,
        "characters" : list_pjs
    })

## AUDIT

### Eve Characters List
@login_required(login_url='/')
def audit_account(request):
    list_pjs = EveCharater.objects.filter(user_character = request.user).all()

    main_pj = list_pjs.filter(main=True).first()
    isk_total = 0
    skill_points_total = 0

    for pj in list_pjs:
        isk_total+= pj.walletMoney
        skill_points_total += pj.totalSkillPoints
        pj.walletMoney = format_number(pj.walletMoney)
        pj.totalSkillPoints = format_number(pj.totalSkillPoints)

    isk_total = format_number(isk_total)
    skill_points_total = format_number(skill_points_total)

    return render(request, "audit/index.html",{
        "main_pj" : main_pj,
        "list_pjs" : list_pjs,
        "isk" : isk_total,
        "skill_points" : skill_points_total
    })

### Skill Plan Checker
@login_required(login_url="/")
def skill_plan_checkers(request):

    list_pj = EveCharater.objects.filter(user_character = request.user).all()
    main_pj = list_pj.filter(main = True).first()
    skillplan_list = Skillplan.objects.all()

    for sp in skillplan_list:
        for pj in list_pj:
            pj_skill = pj.skills
            sp_skills = sp.skills
            status = check_skill(pj_skill, sp_skills)
            
            checklist_obj = Skillplan_CheckList.objects.filter(
                skillPlan = sp,
                character = pj
            ).first()

            if checklist_obj:
                checklist_obj.status = status
            else:
                checklist_obj = Skillplan_CheckList.objects.create(status=status)
                checklist_obj.skillPlan.add(sp)
                checklist_obj.character.add(pj)

            checklist_obj.save()

    checklist = Skillplan_CheckList.objects.filter(character__in = list_pj).all()

    return render(request, "audit/skills/index.html",{
        "main_pj": main_pj,
        "list_pj": list_pj,
        "checklist" : checklist
    })
