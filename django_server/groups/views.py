from django.shortcuts import render
from .models import GroupNotifications
from django.contrib.auth.models import User, Group
from sso.models import Eve_Character
from django.contrib.auth.decorators import login_required


# Create your views here.
def create_notification(group_id,user_id,status):
    group = Group.objects.get(id=group_id)
    user = User.objects.get(id=user_id)

    noti = GroupNotifications.objects.create(status = status)
    noti.group.add(group)
    noti.user.add(user)
    noti.save()
    

# Views

@login_required(login_url="/")
def group_list(request):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)
    groups = Group.objects.exclude(name__in= ["Miembro","Reserva Imperial"]).all()
    notification_list = GroupNotifications.objects.filter(user = request.user).all()

    if request.method == "POST":
        group_id = int(request.POST.get("group_id",0).strip())
        user_id = int(request.POST.get("user_id",0).strip())
        status = int(request.POST.get("status",0).strip())
        if status == 0:
            create_notification(group_id, user_id, status)
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

@login_required(login_url="/")
def group_nofitication_list(request):
    main_pj = Eve_Character.objects.get(main=True, user = request.user)
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
