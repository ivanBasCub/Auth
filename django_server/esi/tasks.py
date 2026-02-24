from celery import shared_task
from .views import fit_list, update_character_skills
from sso.models import Eve_Character
from skillplans.models import Skillplan, Skillplan_CheckList
from web.views import check_skill

def check_skill(pj_skill, skillplan):
        for skill, nivel in skillplan.items():
            if skill not in pj_skill or pj_skill[skill] < nivel:
                return False
        return True

@shared_task
def fits():
    fit_list()

@shared_task
def character_skill_list():
    list_character = Eve_Character.objects.all()
    
    for character in list_character:
        character = update_character_skills(character)
        character.save()

            
@shared_task
def refresh_skillplans():
    list_character = Eve_Character.objects.all()
    skillplan_list = Skillplan.objects.all()
    
    for sp in skillplan_list:
        for char in list_character:
            char_skill = char.skills
            sp_skills = sp.skills
            status = check_skill(char_skill, sp_skills)
            
            checklist_obj = Skillplan_CheckList.objects.filter(
                skillPlan = sp,
                character = char
            ).first()

            if checklist_obj:
                checklist_obj.status = status
            else:
                checklist_obj = Skillplan_CheckList.objects.create(status=status)
                checklist_obj.skillPlan.add(sp)
                checklist_obj.character.add(char)

            checklist_obj.save()