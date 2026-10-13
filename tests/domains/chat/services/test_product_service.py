from app.domains.chat.services.product_service import find_inventory_item


def test_find_inventory_item_by_id():
    inventory = [
        {
            "id": "choco-001",
            "name": "Dark Chocolate",
        },
        {
            "id": "choco-002",
            "name": "White Chocolate",
        },
    ]

    result = find_inventory_item(inventory, "choco-001")

    assert result == {
        "id": "choco-001",
        "name": "Dark Chocolate",
    }


def test_find_inventory_item_by_name():
    inventory = [
        {
            "id": "choco-001",
            "name": "Dark Chocolate",
        },
        {
            "id": "choco-002",
            "name": "White Chocolate",
        },
    ]

    result = find_inventory_item(inventory, "White Chocolate")

    assert result == {
        "id": "choco-002",
        "name": "White Chocolate",
    }


def test_find_inventory_item_normalizes_id_case_and_spaces():
    inventory = [
        {
            "id": "choco-001",
            "name": "Dark Chocolate",
        }
    ]

    result = find_inventory_item(inventory, "  CHOCO-001  ")

    assert result == {
        "id": "choco-001",
        "name": "Dark Chocolate",
    }


def test_find_inventory_item_normalizes_name_case_and_spaces():
    inventory = [
        {
            "id": "choco-001",
            "name": "Dark Chocolate",
        }
    ]

    result = find_inventory_item(inventory, "  dark chocolate  ")

    assert result == {
        "id": "choco-001",
        "name": "Dark Chocolate",
    }


def test_find_inventory_item_returns_none_when_not_found():
    inventory = [
        {
            "id": "choco-001",
            "name": "Dark Chocolate",
        }
    ]

    result = find_inventory_item(inventory, "Milk Chocolate")

    assert result is None


def test_find_inventory_item_returns_none_when_inventory_is_empty():
    result = find_inventory_item([], "Dark Chocolate")

    assert result is None