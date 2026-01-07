from django.shortcuts import render

# Create your views here.
def tranfer_skills(skills):
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

    return skills_dict