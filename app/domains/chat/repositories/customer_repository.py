from datetime import date
from typing import Any, Dict, List

from app.core.database import get_db_session
from app.domains.chat.repositories.models import Customer


def _customer_to_dict(customer: Customer) -> Dict[str, Any]:
    return {
        "customer_id": customer.customer_id,
        "name": customer.name,
        "dob": customer.dob.isoformat(),
        "postcode": customer.postcode,
        "first_line_address": customer.first_line_address,
        "phone_number": customer.phone_number,
        "email": customer.email,
    }


def get_all_customers() -> List[Dict[str, Any]]:
    db = get_db_session()

    try:
        customers = db.query(Customer).order_by(Customer.customer_id).all()
        return [_customer_to_dict(customer) for customer in customers]
    finally:
        db.close()


def find_customer_by_id(customer_id: str) -> Dict[str, Any] | None:
    db = get_db_session()

    try:
        customer = (
            db.query(Customer)
            .filter(Customer.customer_id == customer_id.upper().strip())
            .first()
        )

        if customer is None:
            return None

        return _customer_to_dict(customer)
    finally:
        db.close()


def find_customer_by_email(email: str) -> Dict[str, Any] | None:
    db = get_db_session()

    try:
        customer = (
            db.query(Customer)
            .filter(Customer.email == email.lower().strip())
            .first()
        )

        if customer is None:
            return None

        return _customer_to_dict(customer)
    finally:
        db.close()


def find_customer_by_phone_number(phone_number: str) -> Dict[str, Any] | None:
    db = get_db_session()

    try:
        customer = (
            db.query(Customer)
            .filter(Customer.phone_number == phone_number.strip())
            .first()
        )

        if customer is None:
            return None

        return _customer_to_dict(customer)
    finally:
        db.close()


def create_customer(customer_data: Dict[str, Any]) -> Dict[str, Any]:
    db = get_db_session()

    try:
        customer = Customer(
            customer_id=customer_data["customer_id"],
            name=customer_data["name"],
            dob=date.fromisoformat(customer_data["dob"]),
            postcode=customer_data["postcode"],
            first_line_address=customer_data["first_line_address"],
            phone_number=customer_data["phone_number"],
            email=customer_data["email"],
        )

        db.add(customer)
        db.commit()
        db.refresh(customer)

        return _customer_to_dict(customer)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()