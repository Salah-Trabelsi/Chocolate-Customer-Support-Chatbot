from datetime import datetime
from typing import Any, Dict


def is_order_already_paid(order: Dict[str, Any]) -> bool:
    return order.get("status") == "Paid"


def is_order_waiting_for_payment(order: Dict[str, Any]) -> bool:
    return order.get("status") == "Waiting for payment"


def mark_order_as_paid(
    order: Dict[str, Any],
    payment_id: str,
) -> Dict[str, Any]:
    order["status"] = "Paid"
    order["payment_id"] = payment_id

    return order


def build_payment(
    payment_id: str,
    order_id: str,
    customer_id: str,
    payment_method: str,
    order_summary: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "payment_id": payment_id,
        "order_id": order_id,
        "customer_id": customer_id,
        "status": "Paid",
        "payment_method": payment_method,
        "amounts": order_summary["total_amounts"],
        "total_converted": order_summary["total_converted"],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }