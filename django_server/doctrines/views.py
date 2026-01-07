from django.shortcuts import render
from doctrines.models import *

def create_category(name):
    check = Categories.objects.filter(name=name)

    if check.exists():
        return -1

    category = Categories.objects.create(name = name)
    category.save()

    return 0