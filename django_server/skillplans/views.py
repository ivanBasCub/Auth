from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from sso.models import Eve_Character
from .models import Skillplan, Skillplan_CheckList
from .utils import tranfer_skills

# Skillplan views

# List of skillplans
@login_required(login_url="/")
def skill_plan_list(request):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)
    list_skillplans = Skillplan.objects.all()

    return render(request, "audit/skills/admin.html",{
        "main_pj" : main_pj,
        "skillplans" : list_skillplans
    })
    
# Add a skillplan
@login_required(login_url="/")
def add_skill_plan(request):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)

    if request.method == "POST":
        name = request.POST.get("name","").strip()
        desc = request.POST.get("desc","").strip()
        skills = request.POST.get("skills","").strip()

        skills_dict = tranfer_skills(skills)

        skill_plan = Skillplan.objects.create(
            name = name,
            desc = desc,
            skills = skills_dict
        )
        skill_plan.save()

        return redirect("/auth/admin/skillplans/")
    else:
        return render(request, "audit/skills/addskillplan.html",{
            "main_pj" : main_pj
        })

# Modify a skillplan
@login_required(login_url="/")
def edit_skill_plan(request, skillplanid):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)
    sp = Skillplan.objects.get(id = skillplanid)

    if request.method == "POST":
        name = request.POST.get("name","").strip()
        desc = request.POST.get("desc","").strip()
        skills = request.POST.get("skills","").strip()

        if skills != "":
            skills_dict = tranfer_skills(skills)
            sp.skills = skills_dict
        
        sp.name = name
        sp.desc = desc
        sp.save()

        return redirect("/auth/admin/skillplans/")

    return render(request, "audit/skills/modskillplan.html",{
        "main_pj" : main_pj,
        "sp": sp
    })
    
# Delete a skillplan
@login_required(login_url="/")
def del_skill_plan(request, skillplanid):
    try:
        sp = Skillplan.objects.get(id = skillplanid)
        Skillplan_CheckList.objects.filter(skillPlan = sp).delete()
        sp.delete()
    except Skillplan.DoesNotExist:
        pass
    return redirect("/auth/admin/skillplans/")