from typing import Any, Dict, List

from app.core.database import get_db_session
from app.domains.chat.repositories.models import Order, OrderItem


def _order_to_dict(order: Order, order_items: List[OrderItem]) -> Dict[str, Any]:
    return {
        "order_id": order.order_id,
        "customer_id": order.customer_id,
        "status": order.status,
        "payment_id": order.payment_id,
        "items": [item.product_id for item in order_items],
        "item_names": [item.product_name for item in order_items],
        "quantity": [item.quantity for item in order_items],
    }


def get_all_orders() -> List[Dict[str, Any]]:
    db = get_db_session()

    try:
        orders = db.query(Order).order_by(Order.order_id).all()

        result = []
        for order in orders:
            order_items = (
                db.query(OrderItem)
                .filter(OrderItem.order_id == order.order_id)
                .order_by(OrderItem.id)
                .all()
            )

            result.append(_order_to_dict(order, order_items))

        return result
    finally:
        db.close()


def find_order_by_id_from_db(order_id: str) -> Dict[str, Any] | None:
    db = get_db_session()

    try:
        normalized_order_id = order_id.upper().strip()

        order = (
            db.query(Order)
            .filter(Order.order_id == normalized_order_id)
            .first()
        )

        if order is None:
            return None

        order_items = (
            db.query(OrderItem)
            .filter(OrderItem.order_id == order.order_id)
            .order_by(OrderItem.id)
            .all()
        )

        return _order_to_dict(order, order_items)
    finally:
        db.close()


def find_orders_by_customer_id_from_db(customer_id: str) -> List[Dict[str, Any]]:
    db = get_db_session()

    try:
        normalized_customer_id = customer_id.upper().strip()

        orders = (
            db.query(Order)
            .filter(Order.customer_id == normalized_customer_id)
            .order_by(Order.order_id)
            .all()
        )

        result = []
        for order in orders:
            order_items = (
                db.query(OrderItem)
                .filter(OrderItem.order_id == order.order_id)
                .order_by(OrderItem.id)
                .all()
            )

            result.append(_order_to_dict(order, order_items))

        return result
    finally:
        db.close()


def create_order_in_db(order_data: Dict[str, Any]) -> Dict[str, Any]:
    db = get_db_session()

    try:
        order = Order(
            order_id=order_data["order_id"],
            customer_id=order_data["customer_id"],
            status=order_data["status"],
            payment_id=order_data.get("payment_id"),
        )

        db.add(order)

        items = order_data.get("items", [])
        item_names = order_data.get("item_names", [])
        quantities = order_data.get("quantity", [])

        for index, product_id in enumerate(items):
            order_item = OrderItem(
                order_id=order_data["order_id"],
                product_id=product_id,
                product_name=item_names[index] if index < len(item_names) else product_id,
                quantity=quantities[index] if index < len(quantities) else 1,
            )

            db.add(order_item)

        db.commit()

        return order_data

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def update_order_in_db(order_data: Dict[str, Any]) -> Dict[str, Any]:
    db = get_db_session()

    try:
        order = (
            db.query(Order)
            .filter(Order.order_id == order_data["order_id"])
            .first()
        )

        if order is None:
            raise ValueError(f"Order {order_data['order_id']} was not found.")

        order.status = order_data["status"]
        order.payment_id = order_data.get("payment_id")

        db.commit()

        return order_data

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()