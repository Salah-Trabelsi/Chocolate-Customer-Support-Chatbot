from typing import Any, Dict, List

from app.core.database import get_db_session
from app.domains.chat.repositories.models import Payment


def _payment_to_dict(payment: Payment) -> Dict[str, Any]:
    return {
        "payment_id": payment.payment_id,
        "order_id": payment.order_id,
        "customer_id": payment.customer_id,
        "status": payment.status,
        "payment_method": payment.payment_method,
        "amounts": payment.amounts,
        "total_converted": payment.total_converted,
        "created_at": payment.created_at.isoformat() if payment.created_at else None,
    }


def get_all_payments() -> List[Dict[str, Any]]:
    db = get_db_session()

    try:
        payments = db.query(Payment).order_by(Payment.payment_id).all()
        return [_payment_to_dict(payment) for payment in payments]
    finally:
        db.close()


def find_payment_by_id(payment_id: str) -> Dict[str, Any] | None:
    db = get_db_session()

    try:
        normalized_payment_id = payment_id.upper().strip()

        payment = (
            db.query(Payment)
            .filter(Payment.payment_id == normalized_payment_id)
            .first()
        )

        if payment is None:
            return None

        return _payment_to_dict(payment)
    finally:
        db.close()


def find_payments_by_order_id(order_id: str) -> List[Dict[str, Any]]:
    db = get_db_session()

    try:
        normalized_order_id = order_id.upper().strip()

        payments = (
            db.query(Payment)
            .filter(Payment.order_id == normalized_order_id)
            .order_by(Payment.payment_id)
            .all()
        )

        return [_payment_to_dict(payment) for payment in payments]
    finally:
        db.close()


def create_payment_in_db(payment_data: Dict[str, Any]) -> Dict[str, Any]:
    db = get_db_session()

    try:
        payment = Payment(
            payment_id=payment_data["payment_id"],
            order_id=payment_data["order_id"],
            customer_id=payment_data["customer_id"],
            status=payment_data["status"],
            payment_method=payment_data["payment_method"],
            amounts=payment_data["amounts"],
            total_converted=payment_data["total_converted"],
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        return _payment_to_dict(payment)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()