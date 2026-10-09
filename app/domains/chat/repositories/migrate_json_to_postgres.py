import json
from datetime import date
from pathlib import Path

from app.core.database import Base, engine, get_db_session
from app.domains.chat.repositories.models import Customer, Order, OrderItem, Payment

PROJECT_ROOT = Path(__file__).resolve().parents[4]

CUSTOMERS_FILE_PATH = PROJECT_ROOT / "customers_database.json"
ORDERS_FILE_PATH = PROJECT_ROOT / "orders_database.json"
PAYMENTS_FILE_PATH = PROJECT_ROOT / "payments_database.json"


def load_json_file(file_path: Path, default_data):
    if not file_path.exists():
        return default_data

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def clear_existing_data(db):
    db.query(Payment).delete()
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(Customer).delete()
    db.commit()


def migrate_customers(db):
    customers = load_json_file(CUSTOMERS_FILE_PATH, [])

    for customer in customers:
        db_customer = Customer(
            customer_id=customer["customer_id"],
            name=customer["name"],
            dob=parse_date(customer["dob"]),
            postcode=customer["postcode"],
            first_line_address=customer["first_line_address"],
            phone_number=customer["phone_number"],
            email=customer["email"],
        )

        db.add(db_customer)

    db.commit()
    print(f"Migrated customers: {len(customers)}")


def migrate_orders(db):
    orders = load_json_file(ORDERS_FILE_PATH, [])

    for order in orders:
        db_order = Order(
            order_id=order["order_id"],
            customer_id=order["customer_id"],
            status=order["status"],
            payment_id=order.get("payment_id"),
        )

        db.add(db_order)

        items = order.get("items", [])
        item_names = order.get("item_names", [])
        quantities = order.get("quantity", [])

        for index, product_id in enumerate(items):
            product_name = (
                item_names[index]
                if index < len(item_names)
                else product_id
            )

            quantity = (
                quantities[index]
                if index < len(quantities)
                else 1
            )

            db_order_item = OrderItem(
                order_id=order["order_id"],
                product_id=product_id,
                product_name=product_name,
                quantity=quantity,
            )

            db.add(db_order_item)

    db.commit()
    print(f"Migrated orders: {len(orders)}")


def migrate_payments(db):
    payments = load_json_file(PAYMENTS_FILE_PATH, [])

    skipped_payments = 0

    for payment in payments:
        amounts = payment.get("amounts", [])

        total_converted = payment.get("total_converted")

        if total_converted is None:
            total_converted = {
                "currency": "EUR",
                "total": 0,
                "total_display": "0.00 €",
                "exchange_rates": {},
                "migration_note": "Missing total_converted in original JSON payment record.",
            }

        db_payment = Payment(
            payment_id=payment["payment_id"],
            order_id=payment["order_id"],
            customer_id=payment["customer_id"],
            status=payment["status"],
            payment_method=payment.get("payment_method", "unknown"),
            amounts=amounts,
            total_converted=total_converted,
        )

        db.add(db_payment)

    db.commit()
    print(f"Migrated payments: {len(payments)}")


def migrate_json_to_postgres():
    Base.metadata.create_all(bind=engine)

    db = get_db_session()

    try:
        clear_existing_data(db)
        migrate_customers(db)
        migrate_orders(db)
        migrate_payments(db)

        print("JSON data migrated to PostgreSQL successfully.")
    except Exception as error:
        db.rollback()
        print("Migration failed:", error)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_json_to_postgres()