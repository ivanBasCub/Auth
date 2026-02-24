from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from sso.models import Eve_Character
from .models import Category, Doctrine, Fit
from .utils import formater, create_category

# DOCTRINES

## USER VIEW

### List of doctrines
@login_required(login_url='/')
def list_doctrines(request):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)
    doctrines = Doctrine.objects.exclude(title = "undoctrine").all()
    doc_categories = Category.objects.filter(type = 1).all()

    return render(request, "doctrine/list.html", {
        "main_pj" : main_pj,
        "list_doctrines" : doctrines,
        "categories" : doc_categories
    })

### Info of a doctrines
@login_required(login_url="/")
def doctrine_info(request, doc_id):
    doctrine = Doctrine.objects.get(id = doc_id)
    main_pj = Eve_Character.objects.get(main=True, user = request.user)
    doctrine_fits = Fit.objects.filter(doctrine = doctrine).all()

    return render(request, "doctrine/info.html",{
        "main_pj" : main_pj,
        "doctrine" : doctrine,
        "fits" : doctrine_fits
    })
    
## ADMIN VIEW

### List of doctrines
@login_required(login_url="/")
def admin_doctrines(request):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)
    list_doctrines = Doctrine.objects.all()
    list_categories = Category.objects.all()

    return render(request, "doctrine/admin.html",{
        "main_pj" : main_pj,
        "list_doctrines" : list_doctrines,
        "list_categories" : list_categories
    })
    
### Add new doctrine
@login_required(login_url="/")
def add_doctrine(request):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)
    doctrine_fits = Fit.objects.all()
    doctrines_categories = Category.objects.filter(type = 1).all()

    if request.method == "POST":
        doctrine_fits = request.POST.getlist("fit")
        doctrine_name = request.POST.get("doctrineTitle","").strip()
        doctrine_desc = request.POST.get("doctrineDesc","").strip()
        doctrine_category = int(request.POST.get("categoty",0))

        if doctrine_name != "":
            new_doctrine = Doctrine.objects.create(title = doctrine_name, desc = doctrine_desc)

            if doctrine_category != 0:
                category = Category.objects.get(id = doctrine_category)
                new_doctrine.docCategory.add(category)

            new_doctrine.save()

            for fit in doctrine_fits:
                try:
                    fit_obj = Fit.objects.get(id = int(fit))
                    fit_obj.doctrine.add(new_doctrine)
                    fit_obj.save()
                except Fit.DoesNotExist:
                    pass

        return redirect("/auth/doctrine/admin/")
    else:
        return render(request, "doctrine/add.html",{
            "main_pj" : main_pj,
            "fits" : doctrine_fits,
            "categories" : doctrines_categories
        })
        
### Edit a exists doctrine
@login_required(login_url="/")
def edit_doctrine(request, doctrine_id):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)
    doctrine = Doctrine.objects.get(id = doctrine_id)
    doctrines_categories = Category.objects.filter(type = 1).all()
    fits = Fit.objects.all()

    if request.method == "POST":
        doctrine_fits = request.POST.getlist("fit")
        doctrine_name = request.POST.get("doctrineTitle","").strip()
        doctrine_desc = request.POST.get("doctrineDesc","").strip()
        doctrine_category = int(request.POST.get("categoty",0))

        if doctrine_name != "":
            doctrine.title = doctrine_name
            doctrine.desc = doctrine_desc
            doctrine.category.clear()

            if doctrine_category != 0:
                category = Category.objects.get(id = doctrine_category)
                doctrine.category.add(category)
            
            doctrine.save()

            for fit in fits:
                if str(fit.id) in doctrine_fits:
                    fit.doctrine.add(doctrine)
                else:
                    fit.doctrine.remove(doctrine)
                
                fit.save()
        
        return redirect("/auth/doctrine/admin/")
    else:
        return render(request, "doctrine/edit.html",{
            "main_pj" : main_pj,
            "doctrine" : doctrine,
            "categories" : doctrines_categories,
            "fits" : fits
        })
        
### Delete a doctrine
@login_required(login_url="/")
def del_doctrine(request, doctrine_id):
    try:
        doctrine = Doctrine.objects.get(id=doctrine_id)
        doctrine.delete()
    except Doctrine.DoesNotExist:
        pass

    return redirect("/auth/doctrine/admin/")

### Add new doctrine category
@login_required(login_url="/")
def add_doctrine_category(request):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)

    if request.method == "POST":
        category_name = request.POST.get("categoryName","").strip()
        category_type = int(request.POST.get("categoryType",0))

        if category_name != "":
            new_category = Category(name=category_name, type=category_type)
            new_category.save()

        return redirect("/auth/doctrine/admin/")

    else:
        return render(request, "doctrine/category/add.html",{
            "main_pj" : main_pj
        })
        
### Mod a doctrine category
def edit_doctrine_category(request, category_id):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)
    category = Category.objects.get(id = category_id)

    if request.method == "POST":
        category_name = request.POST.get("categoryName","").strip()
        category_type = int(request.POST.get("categoryType",0))

        if category_name != "":
            category.name = category_name
            category.type = category_type
            category.save()

        return redirect("/auth/doctrine/admin/")
    else:
        return render(request, "doctrine/category/edit.html",{
            "main_pj" : main_pj,
            "category" : category
        })
        
### Del a doctrine category
def del_doctrine_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
        if category.name != "uncategorized":
            category.delete()
    except Category.DoesNotExist:
        pass

    return redirect("/auth/doctrine/admin/")

# FITS

## USER VIEW

### View Fit
@login_required(login_url="/")
def fit(request, fit_id):
    def items_filter(flag):
        return [item for item in item_list if item.get("flag").startswith(flag)]
    
    def check_skill(pj_skill, fit_skill):
        for skill, nivel in fit_skill.items():
            if skill not in pj_skill or pj_skill[skill] < nivel:
                return False
        return True

    fit_data = Fit.objects.get(id = fit_id)
    list_pj = Eve_Character.objects.filter(user = request.user).all()
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

    return render(request, "doctrine/fit/info.html",{
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

### edit a fit
@login_required(login_url="/")
def edit_fit(request, fit_id):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)
    fit_data = Fit.objects.get(id = fit_id)
    category_list = Category.objects.filter(type=2).all()

    if request.method == "POST":
        fit_name = request.POST.get("nameFit","").strip()
        fit_desc = request.POST.get("fitDesc","").strip()
        fit_category = int(request.POST.get("fitCategory",0))

        if fit_name != "":
            fit_data.name_fit = fit_name
            fit_data.desc = fit_desc
            fit_data.category.clear()

            if fit_category != 0:
                category = Category.objects.get(id = fit_category)
                fit_data.category.add(category)
            
            fit_data.save()

        return redirect(f"/auth/doctrine/fit/{fit_id}/")
    else:
        return render(request, "doctrine/fit/edit.html",{
            "main_pj" : main_pj,
            "fit" : fit_data,
            "categories" : category_list
        })