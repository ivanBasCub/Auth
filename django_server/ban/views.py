from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from sso.models import EveCharater
from django.utils import timezone
from .models import BanCategory, BannedCharacter
from utils.views import create_csv

# LIST OF BANNED CHARACTERS
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
        ban = BannedCharacter.objects.get(id=ban_id)
        ban.delete()
    except BannedCharacter.DoesNotExist:
        pass

    return redirect("/auth/corp/ban/list/")

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

        return redirect("/auth/corp/ban/list/category/")

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

    return redirect("/auth/corp/ban/list/category/")