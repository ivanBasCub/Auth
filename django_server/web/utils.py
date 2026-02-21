from django.conf import settings
import os, csv

def format_number(n):
    sufijos = [(1_000_000_000_000, "T"), (1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")]
    
    for divisor, sufijo in sufijos:
        if abs(n) >= divisor:
            return f"{n / divisor:.2f} {sufijo}"

    return str(n)

def check_skill(pj_skill, skillplan):
        for skill, nivel in skillplan.items():
            if skill not in pj_skill or pj_skill[skill] < nivel:
                return False
        return True

def formater(text, items):
        for item in items:
            if item.get("flag").startswith("HiSlot") or item.get("flag").startswith("MedSlot") or item.get("flag").startswith("LoSlot") or item.get("flag").startswith("RigSlot") or item.get("flag").startswith("SubSystemSlot"):
                text.append(f"{item['itemName']}\n")
            else:
                text.append(f"{item['itemName']} x{item['quantity']}\n")

        text.append("\n")

        return text

def create_csv(data, filename):
    path = os.path.join(settings.BASE_DIR, "static", "csv", filename)
    with open(path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)

    return path
    