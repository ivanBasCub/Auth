from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from sso.models import Eve_Character
from django.utils import timezone
from .models import Category, Character
from utils.views import create_csv

# LIST OF BANNED CHARACTERS
@login_required(login_url="/")
def banlist(request):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)
    banlist = Character.objects.all()
    categories = Category.objects.all()
    
    if request.method == "POST":
        if "csv" in request.POST:
            file_name = "ban_list" + str(timezone.now().strftime("%Y%m%d%H%M%S")) + ".csv"
            list_data = [["PJ Baneado","Motivo","Categoria", "Autor", "Fecha"]]
            for ban in banlist:
                list_data.append(
                    [
                        ban.character.character_name,
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
    
@login_required(login_url="/")
def add_ban(request):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)
    list_pjs = Eve_Character.objects.filter(main = True).all()
    list_categories = Category.objects.all()

    if request.method == "POST":
        pj_id = int(request.POST.get("character_id",0).strip())
        reason = request.POST.get("reason","").strip()
        pj = Eve_Character.objects.filter(character_id = pj_id).first()
        category_id = int(request.POST.get("ban_category",0).strip())
        category = Category.objects.filter(id = category_id).first()

        if pj_id != 0 and reason != "":
            try:
                new_ban = Character(character = pj, reason = reason, banned_by = request.user, ban_category = category)
                new_ban.save()
            except Eve_Character.DoesNotExist:
                pass

        return redirect("/auth/corp/ban/list/")
    else:
        return render(request, "ban/request.html",{
            "main_pj" : main_pj,
            "list_pjs" : list_pjs,
            "categories" : list_categories
        })
        
@login_required(login_url="/")
def del_ban(request, ban_id):
    try:
        ban = Character.objects.get(id=ban_id)
        ban.delete()
    except Character.DoesNotExist:
        pass

    return redirect("/auth/corp/ban/list/")

#### List Ban Category
@login_required(login_url="/")
def ban_categories(request):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)
    categories = Category.objects.all()

    return render(request, "ban/category/index.html",{
        "main_pj" : main_pj,
        "categories" : categories
    })

#### Add Ban Cateogory
@login_required(login_url="/")
def add_ban_category(request):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)

    if request.method == "POST":
        category_name = request.POST.get("categoryName","").strip()

        if category_name != "":
            new_category = Category(name=category_name)
            new_category.save()

        return redirect("/auth/corp/ban/list/category/")

    else:
        return render(request, "ban/category/request.html",{
            "main_pj" : main_pj
        })
    
#### Del Ban Cateogory
@login_required(login_url="/")
def del_ban_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
        if category.name != "uncategorized":
            category.delete()
    except Category.DoesNotExist:
        pass

    return redirect("/auth/corp/ban/list/category/")