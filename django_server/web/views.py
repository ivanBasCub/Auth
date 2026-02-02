from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from sso.models import EveCharater
from doctrines.models import Doctrine, FitShip, Categories
from ban.models import BannedCharacter, BanCategory, SuspiciousNotification
from fats.models import Fats, FleetType, SRP, SRPShips, Fats_Character
from fats.views import create_fats, create_srp_request
import esi.views as esi_views
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User, Group
import groups.views as groups_views
from groups.models import GroupNotifications
from skillplans.models import Skillplan, Skillplan_CheckList
from recruitment.models import Applications_access
from django.conf import settings
from django.http import HttpResponse
import os, csv

# ADDITIONAL FUNCTIONS
def format_number(n):
    sufijos = [(1_000_000_000_000, "T"), (1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")]
    
    for divisor, sufijo in sufijos:
        if abs(n) >= divisor:
            return f"{n / divisor:.2f} {sufijo}"

    return str(n)

def check_skill(pj_skill, skillplan):
        for skill, nivel in skillplan.items():
            if skill not in pj_skill or pj_skill[skill] < nivel:
                return False
        return True

def formater(text, items):
        for item in items:
            if item.get("flag").startswith("HiSlot") or item.get("flag").startswith("MedSlot") or item.get("flag").startswith("LoSlot") or item.get("flag").startswith("RigSlot") or item.get("flag").startswith("SubSystemSlot"):
                text.append(f"{item['itemName']}\n")
            else:
                text.append(f"{item['itemName']} x{item['quantity']}\n")

        text.append("\n")

        return text

def create_csv(data, filename):
    path = os.path.join(settings.BASE_DIR, "static", "csv", filename)
    with open(path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)

    return path
    

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

## FLEETS

### DOCTRINES

#### Doctrine List
@login_required(login_url='/')
def fittings(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    doctrines = Doctrine.objects.exclude(doctitle = "undoctrine").all()
    doc_categories = Categories.objects.filter(type = 1).all()

    return render(request, "doctrine/doctrinelist.html", {
        "main_pj" : main_pj,
        "list_doctrines" : doctrines,
        "categories" : doc_categories
    })

#### Doctrine Info
@login_required(login_url="/")
def doctrine(request, doc_id):
    doctrine = Doctrine.objects.get(id = doc_id)
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    doctrine_fits = FitShip.objects.filter(fitDoctrine = doctrine).all()

    return render(request, "doctrine/doctrine.html",{
        "main_pj" : main_pj,
        "doctrine" : doctrine,
        "fits" : doctrine_fits
    })

#### Doctrine Admin
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

#### New Doctrine
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
    
#### Mod Doctrine
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

#### Del Doctrine
@login_required(login_url="/")
def del_doctrine(request, doctrine_id):
    try:
        doctrine = Doctrine.objects.get(id=doctrine_id)
        doctrine.delete()
    except Doctrine.DoesNotExist:
        pass

    return redirect("/auth/fittings/admin/")

### DOCTRINES CATEGORIES

#### Add Doctrine category
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
    
#### Mod Doctrine category
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
    
#### Del Doctrine category
@login_required(login_url="/")
def del_category(request, category_id):
    try:
        category = Categories.objects.get(id=category_id)
        if category.name != "uncategorized":
            category.delete()
    except Categories.DoesNotExist:
        pass

    return redirect("/auth/fittings/admin/")

### FATS

#### View FAT list
@login_required(login_url="/")
def fat_list(request):
    limit_30_days = timezone.now() - timedelta(days=30)

    list_pj = EveCharater.objects.filter(user_character = request.user).all()
    main_pj = list_pj.filter(main=True).first()
    fats = Fats.objects.filter(date__gte = limit_30_days).order_by('date').all()
    fat_list = Fats_Character.objects.filter(fat__in = fats, character__in = list_pj).all()

    return render(request, "fat/fatlist.html",{
        "main_pj" : main_pj,
        "list_pj" : list_pj,
        "fats" : fat_list
    })

#### Create FAT
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

### FITS

#### Fit view
@login_required(login_url="/")
def fit(request, fit_id):
    def items_filter(flag):
        return [item for item in item_list if item.get("flag").startswith(flag)]
    
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

#### Mod Fit
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

## CORP

### SUSPICIOUS TRANSFERENCES

#### View Suspicious Notification list
@login_required(login_url="/")
def suspicious_notification_list(request):
    limit_30_days = timezone.now() - timedelta(days=30)

    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    notifications = SuspiciousNotification.objects.filter(date__gte = limit_30_days).all()
    SuspiciousNotification.objects.filter(date__lt=limit_30_days).delete()
    pj_suspicious = EveCharater.objects.filter(
        suspiciousnotification__in=notifications
    ).distinct()

    if request.method == "POST":
        if "csv" in request.POST:
            file_name = "suspicious_transfer" + str(timezone.now().strftime("%Y%m%d%H%M%S")) + ".csv"
            list_data = [["PJ","Sospechoso","Cantidad", "Fecha"]]
            for nt in notifications:
                list_data.append(
                    [
                        nt.character.characterName,
                        nt.target,
                        nt.amount,
                        nt.date.strftime("%Y-%m-%d")
                    ]
                )
            create_csv(list_data, file_name)

            return redirect(f"/static/csv/{file_name}")
        
    for n in notifications:
        n.amount = format_number(n.amount)

    return render(request, "corp/transactions/index.html",{
        'main_pj' : main_pj,
        "notifications" : notifications,
        "pj_list": pj_suspicious
    })

### REPORTS

#### Member list
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

#### fats report
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

#### Skillplan Checker
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
    
### Groups Report
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

@login_required(login_url="/")
def report_member_data(request):
    class Asset():
        def __init__(self, item_id, item_name, quantity):
            self.item_id = item_id
            self.item_name = item_name
            self.quantity = quantity
    
    class Transaction():
        def __init__(self, amount, balance, context, reason, ref_type, target, date):
            self.amount = amount
            self.balance = balance
            self.context = context
            self.reason = reason
            self.ref_type = ref_type
            self.target = target
            self.date = date

    if not request.user.groups.filter(name="Director").exists():
        return redirect("/dashboard/")
    
    main_pj = EveCharater.objects.get(main=True, user_character=request.user)
    list_user = User.objects.exclude(username__in=["Adjutora Helgast","admin","root"]).all()
    list_characters = EveCharater.objects.exclude(characterName="Adjutora Helgast").all()
    list_ref_types = ["acceleration_gate_fee","advertisement_listing_fee","agent_donation","agent_location_services","agent_miscellaneous","agent_mission_collateral_paid","agent_mission_collateral_refunded","agent_mission_reward","agent_mission_reward_corporation_tax","agent_mission_time_bonus_reward","agent_mission_time_bonus_reward_corporation_tax","agent_security_services","agent_services_rendered","agents_preward","air_career_program_reward","alliance_maintainance_fee","alliance_registration_fee","allignment_based_gate_toll","asset_safety_recovery_tax","bounty","bounty_prize","bounty_prize_corporation_tax","bounty_prizes","bounty_reimbursement","bounty_surcharge","brokers_fee","clone_activation","clone_transfer","contraband_fine","contract_auction_bid","contract_auction_bid_corp","contract_auction_bid_refund","contract_auction_sold","contract_brokers_fee","contract_brokers_fee_corp","contract_collateral","contract_collateral_deposited_corp","contract_collateral_payout","contract_collateral_refund","contract_deposit","contract_deposit_corp","contract_deposit_refund","contract_deposit_sales_tax","contract_price","contract_price_payment_corp","contract_reversal","contract_reward","contract_reward_deposited","contract_reward_deposited_corp","contract_reward_refund","contract_sales_tax","copying","corporate_reward_payout","corporate_reward_tax","corporation_account_withdrawal","corporation_bulk_payment","corporation_dividend_payment","corporation_liquidation","corporation_logo_change_cost","corporation_payment","corporation_registration_fee","cosmetic_market_component_item_purchase","cosmetic_market_skin_purchase","cosmetic_market_skin_sale","cosmetic_market_skin_sale_broker_fee","cosmetic_market_skin_sale_tax","cosmetic_market_skin_transaction","courier_mission_escrow","cspa","cspaofflinerefund","daily_challenge_reward","daily_goal_payouts","daily_goal_payouts_tax","datacore_fee","dna_modification_fee","docking_fee","duel_wager_escrow","duel_wager_payment","duel_wager_refund","ess_escrow_transfer","external_trade_delivery","external_trade_freeze","external_trade_thaw","factory_slot_rental_fee","flux_payout","flux_tax","flux_ticket_repayment","flux_ticket_sale","freelance_jobs_broadcasting_fee","freelance_jobs_duration_fee","freelance_jobs_escrow_refund","freelance_jobs_reward","freelance_jobs_reward_corporation_tax","freelance_jobs_reward_escrow","gm_cash_transfer","gm_plex_fee_refund","industry_job_tax","infrastructure_hub_maintenance","inheritance","insurance","insurgency_corruption_contribution_reward","insurgency_suppression_contribution_reward","item_trader_payment","jump_clone_activation_fee","jump_clone_installation_fee","kill_right_fee","lp_store","manufacturing","market_escrow","market_fine_paid","market_provider_tax","market_transaction","medal_creation","medal_issued","milestone_reward_payment","mission_completion","mission_cost","mission_expiration","mission_reward","office_rental_fee","operation_bonus","opportunity_reward","planetary_construction","planetary_export_tax","planetary_import_tax","player_donation","player_trading","project_discovery_reward","project_discovery_tax","project_payouts","reaction","redeemed_isk_token","release_of_impounded_property","repair_bill","reprocessing_tax","researching_material_productivity","researching_technology","researching_time_productivity","resource_wars_reward","reverse_engineering","season_challenge_reward","security_processing_fee","shares","skill_purchase","skyhook_claim_fee","sovereignity_bill","store_purchase","store_purchase_refund","structure_gate_jump","transaction_tax","under_construction","upkeep_adjustment_fee","war_ally_contract","war_fee","war_fee_surrender"]
    
    for user in list_user:
        user.username = user.username.replace("_", " ")
        
    if request.method == "POST":
        char_id = int(request.POST.get("char", 0))
        option = int(request.POST.get("option", 0))
        char = EveCharater.objects.filter(id=char_id).first()
        grouped_assets = {}

        if option == 1:
            data = esi_views.character_assets(char)

            for item in data:
                type_id = item["type_id"]
                quantity = item["quantity"]

                if type_id not in grouped_assets:
                    grouped_assets[type_id] = {
                        "item_id": type_id,
                        "item_name": esi_views.item_name(type_id),
                        "quantity": quantity,
                    }
                else:
                    grouped_assets[type_id]["quantity"] += quantity

            assets = []
            for data in grouped_assets.values():
                assets.append(Asset(
                    item_id=data["item_id"],
                    item_name=data["item_name"],
                    quantity=data["quantity"],
                ))

            if "csv" in request.POST:
                filename = f"assets_{char.characterName}_{timezone.now().strftime('%Y%m%d%H%M%S')}.csv"
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'

                writer = csv.writer(response)
                writer.writerow(["Item ID", "Item Name", "Quantity"])

                for a in assets:
                    writer.writerow([a.item_id, a.item_name, a.quantity])

                return response

            return render(request, "corp/reports/member_data.html", {
                "main_pj": main_pj,
                "list_user": list_user,
                "char": char,
                "list_characters": list_characters,
                "assets": assets,
                "list_ref_types":list_ref_types
            })

        else:
            ref_filter = request.POST.get("ref_filter")
            data = esi_views.character_wallet_journal(char)
            transactions = []

            for trans in data:
                if trans["ref_type"] == ref_filter or ref_filter == "":
                    amount = format_number(trans["amount"])
                    balance = format_number(trans["balance"])
                    context = trans.get("context_id_type", "").split("_")[0]
                    date = trans.get("date", "")
                    reason = trans.get("description", "")
                    ref = trans.get("ref_type", "").replace("_", " ")

                    if trans["first_party_id"] != char.characterId:
                        target = trans["first_party_id"]
                    else:
                        target = trans["second_party_id"]
                        
                    target = esi_views.info_transfer_target_name(target)

                    transactions.append(Transaction(
                        amount=amount,
                        balance=balance,
                        context=context,
                        reason=reason,
                        ref_type=ref,
                        target=target,
                        date=date
                    ))

            if "csv" in request.POST:
                filename = f"transactions_{char.characterName}_{timezone.now().strftime('%Y%m%d%H%M%S')}.csv"
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'

                writer = csv.writer(response)
                writer.writerow(["Amount", "Balance", "Context", "Reason", "Ref Type", "Target", "Date"])

                for t in transactions:
                    writer.writerow([
                        t.amount, t.balance, t.context, t.reason,
                        t.ref_type, t.target, t.date
                    ])

                return response

            return render(request, "corp/reports/member_data.html", {
                "main_pj": main_pj,
                "list_user": list_user,
                "char": char,
                "list_characters": list_characters,
                "transactions": transactions,
                "list_ref_types":list_ref_types
            })

    return render(request, "corp/reports/member_data.html", {
        "main_pj": main_pj,
        "list_user": list_user,
        "list_characters": list_characters,
        "list_ref_types":list_ref_types
    })

    
### BANS

#### Ban list
@login_required(login_url="/")
def banlist(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    banlist = BannedCharacter.objects.all()
    categories = BanCategory.objects.all()
    
    if request.method == "POST":
        if "csv" in request.POST:
            file_name = "ban_list" + str(timezone.now().strftime("%Y%m%d%H%M%S")) + ".csv"
            list_data = [["PJ Baneado","Motivo","Categoria", "Autor", "Fecha"]]
            for ban in banlist:
                list_data.append(
                    [
                        ban.character_name,
                        ban.reason,
                        ban.ban_category.name if ban.ban_category else "uncategorized",
                        ban.banned_by.username.replace('_',' '),
                        ban.ban_date.strftime("%Y-%m-%d")
                    ]
                )
            create_csv(list_data, file_name)

            return redirect(f"/static/csv/{file_name}")

    return render(request, "ban/index.html",{
        "main_pj" : main_pj,
        "banlist" : banlist,
        "categories" : categories
    })

#### Add ban
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
        return render(request, "ban/request.html",{
            "main_pj" : main_pj,
            "list_pjs" : list_pjs,
            "categories" : list_categories
        })

#### Del ban
@login_required(login_url="/")
def del_ban(request, ban_id):
    try:
        ban = BannedCharacter.objects.get(id=ban_id)
        ban.delete()
    except BannedCharacter.DoesNotExist:
        pass

    return redirect("/auth/corp/banlist/")

### BAN CATEGORIES

#### List Ban Categories
@login_required(login_url="/")
def ban_categories(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    categories = BanCategory.objects.all()

    return render(request, "ban/category/index.html",{
        "main_pj" : main_pj,
        "categories" : categories
    })

#### Add Ban Cateogory
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
        return render(request, "ban/category/request.html",{
            "main_pj" : main_pj
        })
    
#### Del Ban Cateogory
@login_required(login_url="/")
def del_ban_category(request, category_id):
    try:
        category = BanCategory.objects.get(id=category_id)
        if category.name != "uncategorized":
            category.delete()
    except BanCategory.DoesNotExist:
        pass

    return redirect("/auth/corp/banlist/categories/")

### USERS

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

## GROUPS

### View groups list
@login_required(login_url="/")
def group_list(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    groups = Group.objects.exclude(name__in= ["Miembro","Reserva Imperial"]).all()
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

### View group application list
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

## SKILLPLANS

### View SkillPlan List
@login_required(login_url="/")
def skill_plan_list(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    list_skillplans = Skillplan.objects.all()

    return render(request, "audit/skills/admin.html",{
        "main_pj" : main_pj,
        "skillplans" : list_skillplans
    })

### Add SkillPlan
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

### Mod SkillPlan
@login_required(login_url="/")
def mod_skill_plan(request, skillplanid):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    sp = Skillplan.objects.get(id = skillplanid)

    if request.method == "POST":
        name = request.POST.get("name","").strip()
        desc = request.POST.get("desc","").strip()
        skills = request.POST.get("skills","").strip()

        if skills != "":
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
            sp.skills = skills_dict
        
        sp.name = name
        sp.desc = desc
        sp.save()

        return redirect("/auth/admin/skillplans/")

    return render(request, "audit/skills/modskillplan.html",{
        "main_pj" : main_pj,
        "sp": sp
    })

### Del SkillPlan
@login_required(login_url="/")
def del_skill_plan(request, skillplanid):
    sp = Skillplan.objects.get(id = skillplanid)
    checklist = Skillplan_CheckList.objects.filter(skillPlan = sp).delete()
    sp.delete()
    return redirect("/auth/admin/skillplans/")

## SRP

### Index SRP
@login_required(login_url="/")
def srp_index(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    list_srp = SRP.objects.all()
    total_cost = 0
    for srp in list_srp:
        total_cost += srp.srp_cost
        srp.srp_cost = format_number(srp.srp_cost)
        srp.pending_requests = SRPShips.objects.filter(srp = srp, status = 0).count()

    total_cost = format_number(total_cost)

    return render(request,"srp/index.html",{
        "main_pj" : main_pj,
        "total_cost" : total_cost,
        "list_srp": list_srp
    })

### Request SRP
@login_required(login_url="/")
def srp_request(request, srp_id):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    srp = SRP.objects.get(srp_id = srp_id)
    
    if request.method == "POST":
        zkill_link = request.POST.get("zkill","").strip()
        if zkill_link != "":
            zkill_id = zkill_link.strip("/").split("/")[-1]
            create_srp_request(zkill_id, srp)

            return redirect(f"/auth/srp/{srp_id}/view/")

    return render(request,"srp/request.html",{
        "main_pj" : main_pj,
        "srp" : srp
    })

### View SRP
@login_required(login_url="/")
def srp_view(request, srp_id):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    srp = SRP.objects.get(srp_id = srp_id)
    list_srp_ships = SRPShips.objects.filter(srp = srp).all()
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
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)

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
            srp_request = SRPShips.objects.get(id = srp_request_id)
            srp_request.status = status
            srp_request.save()

        if srp_status != 0:
            srp = SRP.objects.get(srp_id = srp_id)
            srp.status = srp_status
            srp.save()

            return redirect("/auth/srp/")

    srp = SRP.objects.get(srp_id = srp_id)
    list_srp_ships = SRPShips.objects.filter(srp = srp, status = 0).all()
    check_srp_list = SRPShips.objects.filter(srp = srp).exclude(status = 0).all()

    return render(request,"srp/admin.html",{
        "main_pj" : main_pj,
        "list_srp_ships" : list_srp_ships,
        "check_srp_list" : check_srp_list
    })
    
# RECRUITMENT

## List of Access applications
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

## Request of old players
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

### Fridge
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