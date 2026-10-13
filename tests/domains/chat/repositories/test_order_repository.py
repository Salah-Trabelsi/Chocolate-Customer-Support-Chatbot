import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.domains.chat.repositories import order_repository
from app.domains.chat.repositories.models import Order, OrderItem


@pytest.fixture()
def test_db_session(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db_session():
        return TestingSessionLocal()

    monkeypatch.setattr(
        order_repository,
        "get_db_session",
        override_get_db_session,
    )

    yield TestingSessionLocal


def create_test_order(db_session_factory):
    db = db_session_factory()

    order = Order(
        order_id="ORD001",
        customer_id="CUST001",
        status="Waiting for payment",
        payment_id=None,
    )

    order_item_1 = OrderItem(
        order_id="ORD001",
        product_id="choco-001",
        product_name="Dark Chocolate",
        quantity=2,
    )

    order_item_2 = OrderItem(
        order_id="ORD001",
        product_id="choco-002",
        product_name="White Chocolate",
        quantity=1,
    )

    db.add(order)
    db.add(order_item_1)
    db.add(order_item_2)
    db.commit()
    db.close()


def test_order_to_dict_returns_order_data():
    order = Order(
        order_id="ORD001",
        customer_id="CUST001",
        status="Waiting for payment",
        payment_id=None,
    )

    order_items = [
        OrderItem(
            order_id="ORD001",
            product_id="choco-001",
            product_name="Dark Chocolate",
            quantity=2,
        ),
        OrderItem(
            order_id="ORD001",
            product_id="choco-002",
            product_name="White Chocolate",
            quantity=1,
        ),
    ]

    result = order_repository._order_to_dict(order, order_items)

    assert result == {
        "order_id": "ORD001",
        "customer_id": "CUST001",
        "status": "Waiting for payment",
        "payment_id": None,
        "items": ["choco-001", "choco-002"],
        "item_names": ["Dark Chocolate", "White Chocolate"],
        "quantity": [2, 1],
    }


def test_get_all_orders_returns_orders_with_items(test_db_session):
    create_test_order(test_db_session)

    result = order_repository.get_all_orders()

    assert result == [
        {
            "order_id": "ORD001",
            "customer_id": "CUST001",
            "status": "Waiting for payment",
            "payment_id": None,
            "items": ["choco-001", "choco-002"],
            "item_names": ["Dark Chocolate", "White Chocolate"],
            "quantity": [2, 1],
        }
    ]


def test_find_order_by_id_from_db_returns_order(test_db_session):
    create_test_order(test_db_session)

    result = order_repository.find_order_by_id_from_db("  ord001  ")

    assert result == {
        "order_id": "ORD001",
        "customer_id": "CUST001",
        "status": "Waiting for payment",
        "payment_id": None,
        "items": ["choco-001", "choco-002"],
        "item_names": ["Dark Chocolate", "White Chocolate"],
        "quantity": [2, 1],
    }


def test_find_order_by_id_from_db_returns_none_when_not_found(test_db_session):
    result = order_repository.find_order_by_id_from_db("ORD999")

    assert result is None


def test_find_orders_by_customer_id_from_db_returns_customer_orders(test_db_session):
    create_test_order(test_db_session)

    db = test_db_session()

    second_order = Order(
        order_id="ORD002",
        customer_id="CUST002",
        status="Waiting for payment",
        payment_id=None,
    )

    db.add(second_order)
    db.commit()
    db.close()

    result = order_repository.find_orders_by_customer_id_from_db("  cust001  ")

    assert result == [
        {
            "order_id": "ORD001",
            "customer_id": "CUST001",
            "status": "Waiting for payment",
            "payment_id": None,
            "items": ["choco-001", "choco-002"],
            "item_names": ["Dark Chocolate", "White Chocolate"],
            "quantity": [2, 1],
        }
    ]


def test_find_orders_by_customer_id_from_db_returns_empty_list_when_not_found(
    test_db_session,
):
    result = order_repository.find_orders_by_customer_id_from_db("CUST999")

    assert result == []


def test_create_order_in_db_creates_order_and_items(test_db_session):
    order_data = {
        "order_id": "ORD001",
        "customer_id": "CUST001",
        "status": "Waiting for payment",
        "payment_id": None,
        "items": ["choco-001", "choco-002"],
        "item_names": ["Dark Chocolate", "White Chocolate"],
        "quantity": [2, 1],
    }

    result = order_repository.create_order_in_db(order_data)

    assert result == order_data

    db = test_db_session()
    order = db.query(Order).filter(Order.order_id == "ORD001").first()
    order_items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == "ORD001")
        .order_by(OrderItem.id)
        .all()
    )
    db.close()

    assert order is not None
    assert order.customer_id == "CUST001"
    assert len(order_items) == 2
    assert order_items[0].product_id == "choco-001"
    assert order_items[0].product_name == "Dark Chocolate"
    assert order_items[0].quantity == 2
    assert order_items[1].product_id == "choco-002"
    assert order_items[1].product_name == "White Chocolate"
    assert order_items[1].quantity == 1


def test_create_order_in_db_uses_fallback_item_name_and_quantity(test_db_session):
    order_data = {
        "order_id": "ORD001",
        "customer_id": "CUST001",
        "status": "Waiting for payment",
        "items": ["choco-001"],
        "item_names": [],
        "quantity": [],
    }

    result = order_repository.create_order_in_db(order_data)

    assert result == order_data

    db = test_db_session()
    order_item = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == "ORD001")
        .first()
    )
    db.close()

    assert order_item.product_id == "choco-001"
    assert order_item.product_name == "choco-001"
    assert order_item.quantity == 1


def test_update_order_in_db_updates_order_status_and_payment_id(test_db_session):
    create_test_order(test_db_session)

    updated_order = {
        "order_id": "ORD001",
        "customer_id": "CUST001",
        "status": "Paid",
        "payment_id": "PAY001",
        "items": ["choco-001", "choco-002"],
        "item_names": ["Dark Chocolate", "White Chocolate"],
        "quantity": [2, 1],
    }

    result = order_repository.update_order_in_db(updated_order)

    assert result == updated_order

    db = test_db_session()
    order = db.query(Order).filter(Order.order_id == "ORD001").first()
    db.close()

    assert order.status == "Paid"
    assert order.payment_id == "PAY001"


def test_update_order_in_db_raises_error_when_order_not_found(test_db_session):
    updated_order = {
        "order_id": "ORD999",
        "status": "Paid",
        "payment_id": "PAY001",
    }

    with pytest.raises(ValueError, match="Order ORD999 was not found"):
        order_repository.update_order_in_db(updated_order)