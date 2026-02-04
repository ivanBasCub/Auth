from celery import shared_task
from django.contrib.auth.models import User
from sso.models import EveCharater
from .models import Asset, Item
from esi.views import character_assets, item_data, group_data, structure_data

@shared_task
def update_member_assets():
    corp_members = User.objects.filter(groups__name="Miembro")
    list_characters = EveCharater.objects.filter(user_character__in=corp_members)

    # Caches API
    item_cache = {}
    group_cache = {}
    structure_cache = {}

    # Caches BD
    existing_items = {i.eve_id: i for i in Item.objects.all()}

    for char in list_characters:
        data_assets = character_assets(char)
        if not data_assets:
            print(f"[ERROR] No se pudieron obtener assets para {char}")
            continue

        Asset.objects.filter(character=char).delete()

        for asset in data_assets:
            if not isinstance(asset, dict):
                print(f"[WARN] Asset inválido recibido (no es dict): {asset}")
                continue

            type_id = asset.get("type_id")
            if not isinstance(type_id, int) or type_id <= 0:
                print(f"[WARN] Asset con type_id inválido: {asset}")
                continue

            quantity = asset.get("quantity")
            if quantity is None:
                print(f"[WARN] Asset sin quantity: {asset}")
                continue

            location_id = asset.get("location_id")
            if location_id is None:
                print(f"[WARN] Asset sin location_id: {asset}")
                continue

            loc_flag = asset.get("location_flag", "")

            if type_id not in item_cache:
                try:
                    item_cache[type_id] = item_data(type_id)
                except Exception as e:
                    print(f"[ERROR] item_data({type_id}) → {e}")
                    item_cache[type_id] = {}

            data_item = item_cache[type_id]

            item_name = data_item.get("name", f"Unknown Item {type_id}")
            print(f"[INFO] {char.characterName} - {char.user_character.username} - {item_name}")

            if location_id not in structure_cache:
                try:
                    structure_cache[location_id] = structure_data(
                        character=char,
                        structure_id=location_id
                    )
                except Exception:
                    structure_cache[location_id] = {"name": location_id}

            location_name = structure_cache[location_id].get("name", location_id)

            if type_id not in existing_items:
                new_item = Item.objects.create(
                    eve_id=type_id,
                    name=item_name,
                )
                existing_items[type_id] = new_item

            item = existing_items[type_id]
            
            Asset.objects.create(
                character=char,
                item=item,
                quantity=quantity,
                loc_flag=loc_flag,
                location=location_name
            )