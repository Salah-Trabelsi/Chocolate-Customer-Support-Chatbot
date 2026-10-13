from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.domains.chat.repositories import customer_repository
from app.domains.chat.repositories.models import Customer


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
        customer_repository,
        "get_db_session",
        override_get_db_session,
    )

    yield TestingSessionLocal


def create_test_customer(db_session_factory):
    db = db_session_factory()

    customer = Customer(
        customer_id="CUST001",
        name="Ethan Carter",
        dob=date(1990, 5, 12),
        postcode="SW1A 1AA",
        first_line_address="10 Downing Street",
        phone_number="+49123456789",
        email="ethan@example.com",
    )

    db.add(customer)
    db.commit()
    db.close()


def test_customer_to_dict_returns_customer_data():
    customer = Customer(
        customer_id="CUST001",
        name="Ethan Carter",
        dob=date(1990, 5, 12),
        postcode="SW1A 1AA",
        first_line_address="10 Downing Street",
        phone_number="+49123456789",
        email="ethan@example.com",
    )

    result = customer_repository._customer_to_dict(customer)

    assert result == {
        "customer_id": "CUST001",
        "name": "Ethan Carter",
        "dob": "1990-05-12",
        "postcode": "SW1A 1AA",
        "first_line_address": "10 Downing Street",
        "phone_number": "+49123456789",
        "email": "ethan@example.com",
    }


def test_get_all_customers_returns_customers(test_db_session):
    create_test_customer(test_db_session)

    result = customer_repository.get_all_customers()

    assert result == [
        {
            "customer_id": "CUST001",
            "name": "Ethan Carter",
            "dob": "1990-05-12",
            "postcode": "SW1A 1AA",
            "first_line_address": "10 Downing Street",
            "phone_number": "+49123456789",
            "email": "ethan@example.com",
        }
    ]


def test_find_customer_by_id_returns_customer(test_db_session):
    create_test_customer(test_db_session)

    result = customer_repository.find_customer_by_id("cust001")

    assert result == {
        "customer_id": "CUST001",
        "name": "Ethan Carter",
        "dob": "1990-05-12",
        "postcode": "SW1A 1AA",
        "first_line_address": "10 Downing Street",
        "phone_number": "+49123456789",
        "email": "ethan@example.com",
    }


def test_find_customer_by_id_returns_none_when_not_found(test_db_session):
    result = customer_repository.find_customer_by_id("CUST999")

    assert result is None


def test_find_customer_by_email_returns_customer(test_db_session):
    create_test_customer(test_db_session)

    result = customer_repository.find_customer_by_email("  ETHAN@example.com  ")

    assert result["customer_id"] == "CUST001"
    assert result["email"] == "ethan@example.com"


def test_find_customer_by_email_returns_none_when_not_found(test_db_session):
    result = customer_repository.find_customer_by_email("missing@example.com")

    assert result is None


def test_find_customer_by_phone_number_returns_customer(test_db_session):
    create_test_customer(test_db_session)

    result = customer_repository.find_customer_by_phone_number("  +49123456789  ")

    assert result["customer_id"] == "CUST001"
    assert result["phone_number"] == "+49123456789"


def test_find_customer_by_phone_number_returns_none_when_not_found(test_db_session):
    result = customer_repository.find_customer_by_phone_number("+49999999999")

    assert result is None


def test_create_customer_creates_and_returns_customer(test_db_session):
    customer_data = {
        "customer_id": "CUST001",
        "name": "Ethan Carter",
        "dob": "1990-05-12",
        "postcode": "SW1A 1AA",
        "first_line_address": "10 Downing Street",
        "phone_number": "+49123456789",
        "email": "ethan@example.com",
    }

    result = customer_repository.create_customer(customer_data)

    assert result == customer_data

    db = test_db_session()
    customer = db.query(Customer).filter(Customer.customer_id == "CUST001").first()
    db.close()

    assert customer is not None
    assert customer.name == "Ethan Carter"
