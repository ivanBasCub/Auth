from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from sso.models import EveCharater
from doctrines.models import Doctrine, FitShip, Categories
from ban.models import BannedCharacter, BanCategory
from fats.models import Fats, FleetType
from fats.views import create_fats
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User, Group
import groups.views as groups_views
from groups.models import GroupNotifications
from skillplans.models import Skillplan, Skillplan_CheckList

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect("/auth/dashboard/")
    else:
        return render(request, "index.html")

# Vista principal del usuario
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

# Vista de los personajes del usuario
@login_required(login_url='/')
def audit_account(request):
    list_pjs = EveCharater.objects.filter(user_character = request.user).all()

    main_pj = list_pjs.filter(main=True).first()
    isk_total = 0
    skill_points_total = 0

    for pj in list_pjs:
        isk_total+= pj.walletMoney
        skill_points_total += pj.totalSkillPoints
        pj.walletMoney = formatear_numero(pj.walletMoney)
        pj.totalSkillPoints = formatear_numero(pj.totalSkillPoints)

    isk_total = formatear_numero(isk_total)
    skill_points_total = formatear_numero(skill_points_total)

    return render(request, "audit/audit.html",{
        "main_pj" : main_pj,
        "list_pjs" : list_pjs,
        "isk" : isk_total,
        "skill_points" : skill_points_total
    })

# Funcion para formatear numeros
def formatear_numero(n):
    # Lista de sufijos y divisores
    sufijos = [
        (1_000_000_000_000, "T"),  # Trillones
        (1_000_000_000, "B"),      # Billions (miles de millones)
        (1_000_000, "M"),          # Millones
        (1_000, "K")               # Miles
    ]
    
    for divisor, sufijo in sufijos:
        if abs(n) >= divisor:
            return f"{n / divisor:.2f} {sufijo}"
    
    # Si es menor de mil, se devuelve tal cual
    return str(n)

# Zona de Fiteos
@login_required(login_url='/')
def fittings(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    doctrines = Doctrine.objects.exclude(doctitle = "undoctrine").all()
    doc_categories = Categories.objects.filter(type = 1).all()

    return render(request, "doctrine/fittings.html", {
        "main_pj" : main_pj,
        "list_doctrines" : doctrines,
        "categories" : doc_categories
    })

# Vista de una doctrina
@login_required(login_url="/")
def doctrine(request, doc_id):
    doctrine = Doctrine.objects.get(id = doc_id)
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    doctrine_fits = FitShip.objects.filter(fitDoctrine = doctrine).all()

    return render(request, "doctrine/doctrines.html",{
        "main_pj" : main_pj,
        "doctrine" : doctrine,
        "fits" : doctrine_fits
    })

# Vista de un fiteo
@login_required(login_url="/")
def fit(request, fit_id):
    def items_filter(flag):
        return [item for item in item_list if item.get("flag").startswith(flag)]

    def formater(text, items):
        for item in items:
            if item.get("flag").startswith("HiSlot") or item.get("flag").startswith("MedSlot") or item.get("flag").startswith("LoSlot") or item.get("flag").startswith("RigSlot") or item.get("flag").startswith("SubSystemSlot"):
                text.append(f"{item['itemName']}\n")
            else:
                text.append(f"{item['itemName']} x{item['quantity']}\n")

        text.append("\n")

        return text

    def check_skill(pj_skill, fit_skill):
        for skill, nivel in fit_skill.items():
            if skill not in pj_skill or pj_skill[skill] < nivel:
                return False
        return True

    fit_data = FitShip.objects.get(id = fit_id)
    list_pj = EveCharater.objects.filter(user_character = request.user).all()
    main_pj = list_pj.filter(main=True).first()

    for pj in list_pj:
        pj.check_ship = check_skill(pj.skills, fit_data.min_skills)

    item_list = fit_data.items

    hi_items = items_filter("HiSlot")
    hi_slots = f"img/{len(hi_items)}h.png"
    med_items = items_filter("MedSlot")
    med_slots = f"img/{len(med_items)}m.png"
    lo_items = items_filter("LoSlot")
    lo_slots = f"img/{len(lo_items)}l.png"
    rig_items = items_filter("RigSlot")
    rig_slots = f"img/{len(rig_items)}r.png"
    subsystem_items = items_filter("SubSystemSlot")
    cargo_items = items_filter("Cargo")
    drones_items = items_filter("DroneBay")
    fighters_items = items_filter("FighterBay")

    etf_text = [f"[{fit_data.shipName}, {fit_data.nameFit}]","\n"]
    etf_text = formater(etf_text, lo_items)
    etf_text = formater(etf_text, med_items)
    etf_text = formater(etf_text, hi_items)
    etf_text = formater(etf_text, rig_items)
    etf_text = formater(etf_text, subsystem_items)
    etf_text = formater(etf_text, drones_items)
    etf_text = formater(etf_text, fighters_items)
    etf_text = formater(etf_text, cargo_items)

    etf_str = "".join(etf_text)

    return render(request, "doctrine/fit/fit.html",{
        "main_pj" : main_pj,
        "list_pj" : list_pj,
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
        "etf" : etf_str,
        "fit_skills" : fit_data.min_skills
    })

# Zona de administración de doctrinas
@login_required(login_url="/")
def admin_doctrines(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    list_doctrines = Doctrine.objects.all()
    list_categories = Categories.objects.all()

    return render(request, "doctrine/confDoctrines.html",{
        "main_pj" : main_pj,
        "list_doctrines" : list_doctrines,
        "list_categories" : list_categories
    })

# Nueva doctrina
@login_required(login_url="/")
def add_doctrine(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    doctrine_fits = FitShip.objects.all()
    doctrines_categories = Categories.objects.filter(type = 1).all()

    if request.method == "POST":
        doctrine_fits = request.POST.getlist("fit")
        doctrine_name = request.POST.get("doctrineTitle","").strip()
        doctrine_desc = request.POST.get("doctrineDesc","").strip()
        doctrine_category = int(request.POST.get("categoty",0))

        if doctrine_name != "":
            new_doctrine = Doctrine.objects.create(doctitle = doctrine_name, desc = doctrine_desc)

            if doctrine_category != 0:
                category = Categories.objects.get(id = doctrine_category)
                new_doctrine.docCategory.add(category)

            new_doctrine.save()

            for fit in doctrine_fits:
                try:
                    fit_obj = FitShip.objects.get(id = int(fit))
                    fit_obj.fitDoctrine.add(new_doctrine)
                    fit_obj.save()
                except FitShip.DoesNotExist:
                    pass

        return redirect("/auth/fittings/admin/")
    else:
        return render(request, "doctrine/addDoctrine.html",{
            "main_pj" : main_pj,
            "fits" : doctrine_fits,
            "categories" : doctrines_categories
        })

# Modificar doctrina
@login_required(login_url="/")
def mod_doctrine(request, doctrine_id):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    doctrine = Doctrine.objects.get(id = doctrine_id)
    doctrines_categories = Categories.objects.filter(type = 1).all()
    fits = FitShip.objects.all()

    if request.method == "POST":
        doctrine_fits = request.POST.getlist("fit")
        doctrine_name = request.POST.get("doctrineTitle","").strip()
        doctrine_desc = request.POST.get("doctrineDesc","").strip()
        doctrine_category = int(request.POST.get("categoty",0))

        if doctrine_name != "":
            doctrine.doctitle = doctrine_name
            doctrine.desc = doctrine_desc
            doctrine.docCategory.clear()

            if doctrine_category != 0:
                category = Categories.objects.get(id = doctrine_category)
                doctrine.docCategory.add(category)
            
            doctrine.save()

            for fit in fits:
                if str(fit.id) in doctrine_fits:
                    fit.fitDoctrine.add(doctrine)
                else:
                    fit.fitDoctrine.remove(doctrine)
                
                fit.save()
        
        return redirect("/auth/fittings/admin/")
    else:
        return render(request, "doctrine/modDoctrine.html",{
            "main_pj" : main_pj,
            "doctrine" : doctrine,
            "categories" : doctrines_categories,
            "fits" : fits
        })

# Eliminar doctrina
@login_required(login_url="/")
def del_doctrine(request, doctrine_id):
    try:
        doctrine = Doctrine.objects.get(id=doctrine_id)
        doctrine.delete()
    except Doctrine.DoesNotExist:
        pass

    return redirect("/auth/fittings/admin/")

# Añadir categoría
@login_required(login_url="/")
def add_category(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)

    if request.method == "POST":
        category_name = request.POST.get("categoryName","").strip()
        category_type = int(request.POST.get("categoryType",0))

        if category_name != "":
            new_category = Categories(name=category_name, type=category_type)
            new_category.save()

        return redirect("/auth/fittings/admin/")

    else:
        return render(request, "doctrine/category/addCategory.html",{
            "main_pj" : main_pj
        })

# Modificar categoría
@login_required(login_url="/")
def mod_category(request, category_id):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    category = Categories.objects.get(id = category_id)

    if request.method == "POST":
        category_name = request.POST.get("categoryName","").strip()
        category_type = int(request.POST.get("categoryType",0))

        if category_name != "":
            category.name = category_name
            category.type = category_type
            category.save()

        return redirect("/auth/fittings/admin/")
    else:
        return render(request, "doctrine/category/modCategory.html",{
            "main_pj" : main_pj,
            "category" : category
        })

# Eliminar categoría
@login_required(login_url="/")
def del_category(request, category_id):
    try:
        category = Categories.objects.get(id=category_id)
        if category.name != "uncategorized":
            category.delete()
    except Categories.DoesNotExist:
        pass

    return redirect("/auth/fittings/admin/")

# Modificar fiteo
@login_required(login_url="/")
def mod_fit(request, fit_id):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    fit_data = FitShip.objects.get(id = fit_id)
    category_list = Categories.objects.filter(type=2).all()

    if request.method == "POST":
        fit_name = request.POST.get("nameFit","").strip()
        fit_desc = request.POST.get("fitDesc","").strip()
        fit_category = int(request.POST.get("fitCategory",0))

        if fit_name != "":
            fit_data.nameFit = fit_name
            fit_data.desc = fit_desc
            fit_data.fitCategory.clear()

            if fit_category != 0:
                category = Categories.objects.get(id = fit_category)
                fit_data.fitCategory.add(category)
            
            fit_data.save()

        return redirect(f"/auth/fittings/fit/{fit_id}/")
    else:
        return render(request, "doctrine/fit/modFit.html",{
            "main_pj" : main_pj,
            "fit" : fit_data,
            "categories" : category_list
        })
    
# Zona de administración de corp

# Lista de baneos
@login_required(login_url="/")
def banlist(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    banlist = BannedCharacter.objects.all()
    categories = BanCategory.objects.all()
    
    return render(request, "ban/banlist.html",{
        "main_pj" : main_pj,
        "banlist" : banlist,
        "categories" : categories
    })

# Añadir baneo
@login_required(login_url="/")
def add_ban(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    list_pjs = EveCharater.objects.filter(main = True).all()
    list_categories = BanCategory.objects.all()

    if request.method == "POST":
        pj_id = int(request.POST.get("character_id",0).strip())
        reason = request.POST.get("reason","").strip()
        pj = EveCharater.objects.filter(characterId = pj_id).first()
        category_id = int(request.POST.get("ban_category",0).strip())
        category = BanCategory.objects.filter(id = category_id).first()

        if pj_id != 0 and reason != "":
            try:
                new_ban = BannedCharacter(character_id = pj_id, character_name = pj.characterName, reason = reason, banned_by = request.user, ban_category = category)
                new_ban.save()
            except EveCharater.DoesNotExist:
                pass

        return redirect("/auth/corp/banlist/")
    else:
        return render(request, "ban/addBan.html",{
            "main_pj" : main_pj,
            "list_pjs" : list_pjs,
            "categories" : list_categories
        })

# Eliminar baneo  
@login_required(login_url="/")
def del_ban(request, ban_id):
    try:
        ban = BannedCharacter.objects.get(id=ban_id)
        ban.delete()
    except BannedCharacter.DoesNotExist:
        pass

    return redirect("/auth/corp/banlist/")

# Lista de categorías de baneos
@login_required(login_url="/")
def ban_categories(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    categories = BanCategory.objects.all()

    return render(request, "ban/category/banCategoryList.html",{
        "main_pj" : main_pj,
        "categories" : categories
    })

# Añadir categoría de baneo
@login_required(login_url="/")
def add_ban_category(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)

    if request.method == "POST":
        category_name = request.POST.get("categoryName","").strip()

        if category_name != "":
            new_category = BanCategory(name=category_name)
            new_category.save()

        return redirect("/auth/corp/banlist/categories/")

    else:
        return render(request, "ban/category/addBanCategory.html",{
            "main_pj" : main_pj
        })

@login_required(login_url="/")
def del_ban_category(request, category_id):
    try:
        category = BanCategory.objects.get(id=category_id)
        if category.name != "uncategorized":
            category.delete()
    except BanCategory.DoesNotExist:
        pass

    return redirect("/auth/corp/banlist/categories/")

# Vista de Fats
@login_required(login_url="/")
def fat_list(request):
    limit_30_days = timezone.now() - timedelta(days=30)

    list_pj = EveCharater.objects.filter(user_character = request.user).all()
    main_pj = list_pj.filter(main=True).first()
    fats = Fats.objects.filter(character__in = list_pj, date__gte = limit_30_days).order_by('date').all()
    

    return render(request, "fat/fatlist.html",{
        "main_pj" : main_pj,
        "list_pj" : list_pj,
        "fats" : fats
    })

@login_required(login_url="/")
def add_fat(request):
    list_pj = EveCharater.objects.filter(user_character = request.user).all()
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
        return render(request, "fat/addFat.html",{
            "main_pj" : main_pj,
            "list_pj" : list_pj,
            "fleet_types" : fleet_types,
            "doctrines" : doctrines
        })
    
# Vista de Lista de miembros
@login_required(login_url="/")
def member_list(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    members = EveCharater.objects.filter(main= True).all()
    
    for member in members:
        user = User.objects.get(username = member.characterName.replace(' ','_'))
        member.alts_list = EveCharater.objects.filter(user_character = user, main = False).all()
        member.ban = BannedCharacter.objects.filter(character_id = member.characterId).exists()


    return render(request, "corp/member/corpMembersList.html",{
        "main_pj" : main_pj,
        "members" : members
    })

# Vista de los grupos

#Vista de los grupos disponibles
@login_required(login_url="/")
def group_list(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    groups = Group.objects.exclude(name__in= ["Miembro","High-Sec"]).all()
    notification_list = GroupNotifications.objects.filter(user = request.user).all()

    if request.method == "POST":
        group_id = int(request.POST.get("group_id",0).strip())
        user_id = int(request.POST.get("user_id",0).strip())
        status = int(request.POST.get("status",0).strip())
        if status == 0:
            groups_views.create_notification(group_id, user_id, status)
        else:
            remove_group = Group.objects.get(id = group_id)
            user = User.objects.get(id = user_id)
            user.groups.remove(remove_group)
            user.save()
            

    for group in groups:
        notification = GroupNotifications.objects.filter(group = group)
        if notification.exists():
            group.notification = True

    return render(request, "group/listGroups.html", {
        "main_pj": main_pj,
        "groups" : groups,
        "notification_list": notification_list
    })

# Vista para resolver las solicitudes de grupo
@login_required(login_url="/")
def group_nofitication_list(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    list_notifications = GroupNotifications.objects.all()

    if request.method == "POST":
        noti_id = int(request.POST.get("noti_id",0).strip())
        action = int(request.POST.get("action",0).strip())

        notification = GroupNotifications.objects.get(id=noti_id)

        if action == 1:
            user = notification.user.first()
            group = notification.group.first()
            user.groups.add(group)
            user.save()

        notification.delete()

    return render(request, "group/listGroupsNotifications.html",{
        "main_pj": main_pj,
        "list_notifications" : list_notifications
    })

# Vista de usuario para comprobar si tiene completo los skill plans
@login_required(login_url="/")
def skill_plan_checkers(request):
    def check_skill(pj_skill, skillplan):
        for skill, nivel in skillplan.items():
            if skill not in pj_skill or pj_skill[skill] < nivel:
                return False
        return True

    list_pj = EveCharater.objects.filter(user_character = request.user).all()
    main_pj = list_pj.filter(main = True).first()
    skillplan_list = Skillplan.objects.all()

    for sp in skillplan_list:
        for pj in list_pj:
            pj_skill = pj.skills
            sp_skills = sp.skills
            status = check_skill(pj_skill, sp_skills)
            
            checklist_obj = Skillplan_CheckList.objects.filter(
                Skillplan = sp,
                character = pj
            ).first()

            if checklist_obj:
                print(sp.name, " / ", pj.characterName, " / " ,status)
                checklist_obj.status = status
            else:
                checklist_obj = Skillplan_CheckList.objects.create(status=status)
                checklist_obj.Skillplan.add(sp)
                checklist_obj.character.add(pj)

            checklist_obj.save()

    checklist = Skillplan_CheckList.objects.filter(character__in = list_pj).all()

    return render(request, "audit/skills/skillplan.html",{
        "main_pj": main_pj,
        "list_pj": list_pj,
        "checklist" : checklist
    })

# Ver lista de skillsPlans
@login_required(login_url="/")
def skill_plan_list(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    list_skillplans = Skillplan.objects.all()

    return render(request, "audit/skills/skillplanlist.html",{
        "main_pj" : main_pj,
        "skillplans" : list_skillplans
    })

@login_required(login_url="/")
def add_skill_plan(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)

    if request.method == "POST":
        name = request.POST.get("name","").strip()
        desc = request.POST.get("desc","").strip()
        skills = request.POST.get("skills","").strip()

        skills_dict = {}
        for linea in skills.strip().splitlines():
            if linea.strip():
                *nombre, nivel = linea.strip().split()
                nombre_skill = " ".join(nombre)
                nivel = int(nivel)
                # Si ya existe, guardamos el nivel más alto
                if nombre_skill in skills_dict:
                    skills_dict[nombre_skill] = max(skills_dict[nombre_skill], nivel)
                else:
                    skills_dict[nombre_skill] = nivel

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

@login_required(login_url="/")
def mod_skill_plan(request, skillplanid):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    sp = Skillplan.objects.get(id = skillplanid)

    if request.method == "POST":
        name = request.POST.get("name","").strip()
        desc = request.POST.get("desc","").strip()
        skills = request.POST.get("skills","").strip()

        skills_dict = {}
        for linea in skills.strip().splitlines():
            if linea.strip():
                *nombre, nivel = linea.strip().split()
                nombre_skill = " ".join(nombre)
                nivel = int(nivel)
                # Si ya existe, guardamos el nivel más alto
                if nombre_skill in skills_dict:
                    skills_dict[nombre_skill] = max(skills_dict[nombre_skill], nivel)
                else:
                    skills_dict[nombre_skill] = nivel

        sp.name = name
        sp.desc = desc
        sp.skills = skills
        sp.save()

    return render(request, "audit/skills/modskillplan.html",{
        "main_pj" : main_pj,
        "sp": sp
    })

@login_required(login_url="/")
def del_skill_plan(request, skillplanid):
    sp = Skillplan.objects.get(id = skillplanid)
    checklist = Skillplan_CheckList.objects.filter(Skillplan = sp).delete()
    sp.delete()
    return redirect("/auth/admin/skillplans/")