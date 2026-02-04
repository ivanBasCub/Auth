from celery import shared_task
from django.contrib.auth.models import User
from sso.models import EveCharater
from .models import Asset, Item, ItemGroup
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
    existing_groups = {g.eve_id: g for g in ItemGroup.objects.all()}
    existing_items = {i.eve_id: i for i in Item.objects.all()}

    for char in list_characters:
        data_assets = character_assets(char)

        Asset.objects.filter(character=char).delete()

        for asset in data_assets:
            type_id = asset.get("type_id")

            if type_id not in item_cache:
                try:
                    item_cache[type_id] = item_data(type_id)
                except Exception as e:
                    print(f"[ERROR] item_data({type_id}) → {e}")
                    item_cache[type_id] = {}

            data_item = item_cache[type_id]

            # Valores seguros
            item_name = data_item.get("name", f"Unknown Item {type_id}")
            group_id = data_item.get("group_id", 1)

            if group_id not in group_cache:
                try:
                    group_cache[group_id] = group_data(group_id)
                except Exception as e:
                    print(f"[ERROR] group_data({group_id}) → {e}")
                    group_cache[group_id] = {
                        "group_id": 1,
                        "name": "Unknown Group"
                    }

            data_group = group_cache[group_id]

            # Valores seguros
            group_eve_id = data_group.get("group_id", 1)
            group_name = data_group.get("name", "Unknown Group")

            if group_eve_id not in existing_groups:
                new_group = ItemGroup.objects.create(
                    eve_id=group_eve_id,
                    name=group_name
                )
                existing_groups[group_eve_id] = new_group

            group_eve = existing_groups[group_eve_id]

            location_id = asset.get("location_id")

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
                    group=group_eve
                )
                existing_items[type_id] = new_item

            item = existing_items[type_id]

            Asset.objects.create(
                character=char,
                item=item,
                quantity=asset.get("quantity", 0),
                loc_flag=asset.get("location_flag", ""),
                location=location_name
            )