from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.domains.chat.repositories import payment_repository
from app.domains.chat.repositories.models import Payment


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
        payment_repository,
        "get_db_session",
        override_get_db_session,
    )

    yield TestingSessionLocal


def create_test_payment(db_session_factory):
    db = db_session_factory()

    payment = Payment(
        payment_id="PAY001",
        order_id="ORD001",
        customer_id="CUST001",
        status="Paid",
        payment_method="Credit card",
        amounts=[
            {
                "currency": "EUR",
                "total": 20.0,
                "total_display": "20.00 €",
            }
        ],
        total_converted={
            "currency": "EUR",
            "total": 20.0,
            "total_display": "20.00 €",
        },
    )

    db.add(payment)
    db.commit()
    db.close()


def test_payment_to_dict_returns_payment_data():
    created_at = datetime(2026, 1, 1, 12, 30, 0)

    payment = Payment(
        payment_id="PAY001",
        order_id="ORD001",
        customer_id="CUST001",
        status="Paid",
        payment_method="Credit card",
        amounts=[
            {
                "currency": "EUR",
                "total": 20.0,
                "total_display": "20.00 €",
            }
        ],
        total_converted={
            "currency": "EUR",
            "total": 20.0,
            "total_display": "20.00 €",
        },
        created_at=created_at,
    )

    result = payment_repository._payment_to_dict(payment)

    assert result == {
        "payment_id": "PAY001",
        "order_id": "ORD001",
        "customer_id": "CUST001",
        "status": "Paid",
        "payment_method": "Credit card",
        "amounts": [
            {
                "currency": "EUR",
                "total": 20.0,
                "total_display": "20.00 €",
            }
        ],
        "total_converted": {
            "currency": "EUR",
            "total": 20.0,
            "total_display": "20.00 €",
        },
        "created_at": "2026-01-01T12:30:00",
    }


def test_payment_to_dict_returns_none_created_at_when_missing():
    payment = Payment(
        payment_id="PAY001",
        order_id="ORD001",
        customer_id="CUST001",
        status="Paid",
        payment_method="Credit card",
        amounts=[],
        total_converted={},
        created_at=None,
    )

    result = payment_repository._payment_to_dict(payment)

    assert result["created_at"] is None


def test_get_all_payments_returns_payments(test_db_session):
    create_test_payment(test_db_session)

    result = payment_repository.get_all_payments()

    assert len(result) == 1
    assert result[0]["payment_id"] == "PAY001"
    assert result[0]["order_id"] == "ORD001"
    assert result[0]["customer_id"] == "CUST001"
    assert result[0]["status"] == "Paid"


def test_find_payment_by_id_returns_payment(test_db_session):
    create_test_payment(test_db_session)

    result = payment_repository.find_payment_by_id("  pay001  ")

    assert result["payment_id"] == "PAY001"
    assert result["order_id"] == "ORD001"
    assert result["customer_id"] == "CUST001"


def test_find_payment_by_id_returns_none_when_not_found(test_db_session):
    result = payment_repository.find_payment_by_id("PAY999")

    assert result is None


def test_find_payments_by_order_id_returns_matching_payments(test_db_session):
    create_test_payment(test_db_session)

    db = test_db_session()

    second_payment = Payment(
        payment_id="PAY002",
        order_id="ORD002",
        customer_id="CUST002",
        status="Paid",
        payment_method="PayPal",
        amounts=[],
        total_converted={},
    )

    db.add(second_payment)
    db.commit()
    db.close()

    result = payment_repository.find_payments_by_order_id("  ord001  ")

    assert len(result) == 1
    assert result[0]["payment_id"] == "PAY001"
    assert result[0]["order_id"] == "ORD001"


def test_find_payments_by_order_id_returns_empty_list_when_not_found(test_db_session):
    result = payment_repository.find_payments_by_order_id("ORD999")

    assert result == []


def test_create_payment_in_db_creates_and_returns_payment(test_db_session):
    payment_data = {
        "payment_id": "PAY001",
        "order_id": "ORD001",
        "customer_id": "CUST001",
        "status": "Paid",
        "payment_method": "Credit card",
        "amounts": [
            {
                "currency": "EUR",
                "total": 20.0,
                "total_display": "20.00 €",
            }
        ],
        "total_converted": {
            "currency": "EUR",
            "total": 20.0,
            "total_display": "20.00 €",
        },
    }

    result = payment_repository.create_payment_in_db(payment_data)

    assert result["payment_id"] == "PAY001"
    assert result["order_id"] == "ORD001"
    assert result["customer_id"] == "CUST001"
    assert result["status"] == "Paid"
    assert result["payment_method"] == "Credit card"
    assert result["amounts"] == payment_data["amounts"]
    assert result["total_converted"] == payment_data["total_converted"]
    assert result["created_at"] is not None

    db = test_db_session()
    payment = db.query(Payment).filter(Payment.payment_id == "PAY001").first()
    db.close()

    assert payment is not None
    assert payment.order_id == "ORD001"
    assert payment.customer_id == "CUST001"
