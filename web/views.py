from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from sso.models import EveCharater
import esi.views as esi_views
import sso.views as sso_views
from doctrines.models import Doctrine, FitShip, Categories
from django.db.models import Q
from ban.models import BannedCharacter, BanCategory

# Create your views here.
def index(request):
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
    list_alts = list_pjs.filter(main=False).all()

    return render(request, "audit.html",{
        "main_pj" : main_pj,
        "list_pjs" : list_pjs
    })

# Zona de Fiteos
@login_required(login_url='/')
def fittings(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    doctrines = Doctrine.objects.exclude(doctitle = "undoctrine").all()

    return render(request, "fittings.html", {
        "main_pj" : main_pj,
        "list_doctrines" : doctrines
    })

# Vista de una doctrina
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

# Vista de un fiteo
@login_required(login_url="/")
def fit(request, fit_id):
    def items_filter(flag):
        return [item for item in item_list if item.get("flag").startswith(flag)]

    def formater(text, items):
        for item in items:
            if item.get("flag").startswith("HiSlot") or item.get("flag").startswith("MedSlot") or item.get("flag").startswith("LoSlot") or item.get("flag").startswith("RigSlot") or item.get("flag").startswith("SubSystemSlot"):
                text.append(f"{item["itemName"]}\n")
            else:
                text.append(f"{item["itemName"]} x{item["quantity"]}\n")

        text.append("\n")

        return text

    fit_data = FitShip.objects.get(id = fit_id)
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)

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
        "etf" : etf_str
    })

# Zona de administración de doctrinas
@login_required(login_url="/")
def admin_doctrines(request):
    main_pj = EveCharater.objects.get(main=True, user_character = request.user)
    list_doctrines = Doctrine.objects.all()
    list_categories = Categories.objects.all()

    return render(request, "confDoctrines.html",{
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

        print(doctrine_name, doctrine_desc, doctrine_category, doctrine_fits)

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
        return render(request, "addDoctrine.html",{
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

        print(doctrine_category, "/ ", request.POST.get("categoty"))
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
        return render(request, "modDoctrine.html",{
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
        return render(request, "addCategory.html",{
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
        return render(request, "modCategory.html",{
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
        return render(request, "modFit.html",{
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
    
    return render(request, "banlist.html",{
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
        return render(request, "addBan.html",{
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

    return render(request, "banCategoryList.html",{
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
        return render(request, "addBanCategory.html",{
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