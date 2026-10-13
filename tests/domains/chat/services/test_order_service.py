from app.domains.chat.services.order_service import (
    build_order,
    find_order_by_id,
    find_orders_by_customer_id,
    order_belongs_to_customer,
)


def test_find_orders_by_customer_id_returns_matching_orders():
    orders = [
        {
            "order_id": "ORD001",
            "customer_id": "CUST001",
        },
        {
            "order_id": "ORD002",
            "customer_id": "CUST002",
        },
        {
            "order_id": "ORD003",
            "customer_id": "CUST001",
        },
    ]

    result = find_orders_by_customer_id(orders, "CUST001")

    assert result == [
        {
            "order_id": "ORD001",
            "customer_id": "CUST001",
        },
        {
            "order_id": "ORD003",
            "customer_id": "CUST001",
        },
    ]


def test_find_orders_by_customer_id_normalizes_case_and_spaces():
    orders = [
        {
            "order_id": "ORD001",
            "customer_id": "CUST001",
        }
    ]

    result = find_orders_by_customer_id(orders, "  cust001  ")

    assert result == [
        {
            "order_id": "ORD001",
            "customer_id": "CUST001",
        }
    ]


def test_find_orders_by_customer_id_returns_empty_list_when_no_match():
    orders = [
        {
            "order_id": "ORD001",
            "customer_id": "CUST001",
        }
    ]

    result = find_orders_by_customer_id(orders, "CUST999")

    assert result == []


def test_find_order_by_id_returns_matching_order():
    orders = [
        {
            "order_id": "ORD001",
            "customer_id": "CUST001",
        },
        {
            "order_id": "ORD002",
            "customer_id": "CUST002",
        },
    ]

    result = find_order_by_id(orders, "ORD002")

    assert result == {
        "order_id": "ORD002",
        "customer_id": "CUST002",
    }


def test_find_order_by_id_normalizes_case_and_spaces():
    orders = [
        {
            "order_id": "ORD001",
            "customer_id": "CUST001",
        }
    ]

    result = find_order_by_id(orders, "  ord001  ")

    assert result == {
        "order_id": "ORD001",
        "customer_id": "CUST001",
    }


def test_find_order_by_id_returns_none_when_no_match():
    orders = [
        {
            "order_id": "ORD001",
            "customer_id": "CUST001",
        }
    ]

    result = find_order_by_id(orders, "ORD999")

    assert result is None


def test_order_belongs_to_customer_returns_true_for_matching_customer():
    order = {
        "order_id": "ORD001",
        "customer_id": "CUST001",
    }

    result = order_belongs_to_customer(order, "cust001")

    assert result is True


def test_order_belongs_to_customer_returns_false_for_different_customer():
    order = {
        "order_id": "ORD001",
        "customer_id": "CUST001",
    }

    result = order_belongs_to_customer(order, "CUST999")

    assert result is False


def test_build_order_returns_order_with_items_names_and_quantities():
    resolved_items = {
        "choco-001": {
            "name": "Dark Chocolate",
            "quantity": 2,
        },
        "choco-002": {
            "name": "White Chocolate",
            "quantity": 3,
        },
    }

    result = build_order(
        order_id="ORD001",
        customer_id="CUST001",
        resolved_items=resolved_items,
    )

    assert result == {
        "order_id": "ORD001",
        "customer_id": "CUST001",
        "status": "Waiting for payment",
        "items": ["choco-001", "choco-002"],
        "item_names": ["Dark Chocolate", "White Chocolate"],
        "quantity": [2, 3],
    }


def test_build_order_returns_empty_items_when_no_resolved_items():
    result = build_order(
        order_id="ORD001",
        customer_id="CUST001",
        resolved_items={},
    )

    assert result == {
        "order_id": "ORD001",
        "customer_id": "CUST001",
        "status": "Waiting for payment",
        "items": [],
        "item_names": [],
        "quantity": [],
    }
