from typing import Any, Dict, List


def find_orders_by_customer_id(
    orders: List[Dict[str, Any]],
    customer_id: str,
) -> List[Dict[str, Any]]:
    normalized_customer_id = customer_id.upper().strip()

    return [
        order
        for order in orders
        if order["customer_id"].upper().strip() == normalized_customer_id
    ]


def find_order_by_id(
    orders: List[Dict[str, Any]],
    order_id: str,
) -> Dict[str, Any] | None:
    normalized_order_id = order_id.upper().strip()

    return next(
        (
            order
            for order in orders
            if order["order_id"].upper().strip() == normalized_order_id
        ),
        None,
    )


def order_belongs_to_customer(
    order: Dict[str, Any],
    customer_id: str,
) -> bool:
    return order["customer_id"].upper().strip() == customer_id.upper().strip()


def build_order(
    order_id: str,
    customer_id: str,
    resolved_items: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "order_id": order_id,
        "customer_id": customer_id,
        "status": "Waiting for payment",
        "items": list(resolved_items.keys()),
        "item_names": [item["name"] for item in resolved_items.values()],
        "quantity": [item["quantity"] for item in resolved_items.values()],
    }