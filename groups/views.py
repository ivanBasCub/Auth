from django.shortcuts import render
from .models import GroupNotifications
from django.contrib.auth.models import User, Group

# Create your views here.
def create_notification(group_id,user_id,status):
    group = Group.objects.get(id=group_id)
    user = User.objects.get(id=user_id)

    noti = GroupNotifications.objects.create(status = status)
    noti.group.add(group)
    noti.user.add(user)
    noti.save()
    


