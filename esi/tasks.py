from celery import shared_task
from .views import fit_list, update_character_skills
from sso.models import EveCharater
from skillplans.models import Skillplan, Skillplan_CheckList
from web.views import check_skill

@shared_task
def fits():
    fit_list()

@shared_task
def character_skill_list():
    list_character = EveCharater.objects.all()
    skillplan_list = Skillplan.objects.all()
    
    for character in list_character:
        character = update_character_skills(character)
        character.save()

    for sp in skillplan_list:
        for pj in sp.characters.all():
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