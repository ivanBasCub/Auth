from celery import shared_task
from django.contrib.auth.models import User
from sso.models import EveCharater
from .models import Asset, Item, Location
from esi.views import character_assets, item_data, structure_data

@shared_task
def update_member_assets():
    corp_members = User.objects.filter(groups__name="Miembro")
    list_characters = EveCharater.objects.filter(user_character__in=corp_members)

    existing_items = {i.eve_id: i for i in Item.objects.all()}
    existing_locations = {l.eve_id: l for l in Item.objects.all()}

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

            location_id = int(asset.get("location_id"))
            if location_id is None:
                print(f"[WARN] Asset sin location_id: {asset}")
                continue

            loc_flag = asset.get("location_flag", "")
            print(f"[INFO] {char.characterName} - {type_id} - {quantity}")

            if type_id in existing_items:
                item = Item.objects.get(eve_id = type_id)
            else:
                try:
                    data_item = item_data(type_id)
                    item_name = data_item.get("name", f"Unknown Item {type_id}")
                    Item.objects.create(
                        eve_id = type_id,
                        name = item_name
                    )
                
                    item = Item.objects.get(eve_id = type_id)    
                except Exception as e:
                    print(f"[ERROR] data_item({type_id}) → {e}")

            if location_id in existing_locations:
                location = Location.objects.get(eve_id = type_id)
            else:
                try:
                    data_location = structure_data(location_id)
                    location_name = data_location.get("name", f"{type_id}")
                    Location.objects.create(
                        eve_id = type_id,
                        name = location_name
                    )
                
                    location = Location.objects.get(eve_id = type_id)    
                except Exception as e:
                    print(f"[ERROR] data_location({type_id}) → {e}")

            Asset.objects.create(
                character=char,
                item=item,
                quantity=quantity,
                loc_flag=loc_flag,
                location = location
            )
