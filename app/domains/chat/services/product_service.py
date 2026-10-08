from typing import Any, Dict, List

def find_inventory_item(
    inventory: List[Dict[str, Any]],
    item_key: str,
) -> Dict[str, Any] | None:
    normalized_item_key = item_key.lower().strip()

    for item in inventory:
        if item["id"].lower().strip() == normalized_item_key:
            return item

        if item["name"].lower().strip() == normalized_item_key:
            return item

    return None