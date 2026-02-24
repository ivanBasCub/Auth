from .models import  Category

def formater(text, items):
    for item in items:
        if item.get("flag").startswith("HiSlot") or item.get("flag").startswith("MedSlot") or item.get(
                "flag").startswith("LoSlot") or item.get("flag").startswith("RigSlot") or item.get("flag").startswith(
                "SubSystemSlot"):
            text.append(f"{item['itemName']}\n")
        else:
            text.append(f"{item['itemName']} x{item['quantity']}\n")

    text.append("\n")

    return text


def create_category(name):
    check = Category.objects.filter(name=name)

    if check.exists():
        return -1

    category = Category.objects.create(name=name)
    category.save()

    return 0