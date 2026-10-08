from typing import Any, Dict, List


def get_next_order_id(orders: List[Dict[str, Any]]) -> str:
    max_id = 0

    for order in orders:
        order_id = str(order.get("order_id", ""))

        if order_id.startswith("ORD"):
            try:
                number = int(order_id.replace("ORD", ""))
                max_id = max(max_id, number)
            except ValueError:
                continue

    return f"ORD{max_id + 1:03d}"


def get_next_customer_id(customers: List[Dict[str, Any]]) -> str:
    max_id = 0

    for customer in customers:
        customer_id = customer.get("customer_id", "")

        if customer_id.startswith("CUST"):
            try:
                number = int(customer_id.replace("CUST", ""))
                max_id = max(max_id, number)
            except ValueError:
                continue

    return f"CUST{max_id + 1:03d}"


def get_next_payment_id(payments: List[Dict[str, Any]]) -> str:
    max_id = 0

    for payment in payments:
        payment_id = str(payment.get("payment_id", ""))

        if payment_id.startswith("PAY"):
            try:
                number = int(payment_id.replace("PAY", ""))
                max_id = max(max_id, number)
            except ValueError:
                continue

    return f"PAY{max_id + 1:03d}"