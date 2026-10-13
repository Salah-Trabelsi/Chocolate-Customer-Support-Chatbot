from app.domains.chat.services.customer_service import (
    build_customer_profile,
    customer_exists_by_id,
    email_exists,
    find_customer_by_dpa,
    phone_number_exists,
)


def test_find_customer_by_dpa_returns_matching_customer():
    customers = [
        {
            "customer_id": "CUST001",
            "name": "Ethan Carter",
            "postcode": "SW1A 1AA",
            "dob": "1990-05-12",
        }
    ]

    result = find_customer_by_dpa(
        customers=customers,
        name="Ethan Carter",
        postcode="SW1A 1AA",
        year_of_birth=1990,
        month_of_birth=5,
        day_of_birth=12,
    )

    assert result == customers[0]


def test_find_customer_by_dpa_normalizes_name_and_postcode():
    customers = [
        {
            "customer_id": "CUST001",
            "name": "Ethan Carter",
            "postcode": "SW1A 1AA",
            "dob": "1990-05-12",
        }
    ]

    result = find_customer_by_dpa(
        customers=customers,
        name="  ethan carter  ",
        postcode="  sw1a 1aa  ",
        year_of_birth=1990,
        month_of_birth=5,
        day_of_birth=12,
    )

    assert result == customers[0]


def test_find_customer_by_dpa_returns_none_when_no_match():
    customers = [
        {
            "customer_id": "CUST001",
            "name": "Ethan Carter",
            "postcode": "SW1A 1AA",
            "dob": "1990-05-12",
        }
    ]

    result = find_customer_by_dpa(
        customers=customers,
        name="Wrong Name",
        postcode="SW1A 1AA",
        year_of_birth=1990,
        month_of_birth=5,
        day_of_birth=12,
    )

    assert result is None


def test_find_customer_by_dpa_returns_none_when_dob_does_not_match():
    customers = [
        {
            "customer_id": "CUST001",
            "name": "Ethan Carter",
            "postcode": "SW1A 1AA",
            "dob": "1990-05-12",
        }
    ]

    result = find_customer_by_dpa(
        customers=customers,
        name="Ethan Carter",
        postcode="SW1A 1AA",
        year_of_birth=1991,
        month_of_birth=5,
        day_of_birth=12,
    )

    assert result is None


def test_customer_exists_by_id_returns_true_when_customer_exists():
    customers = [
        {
            "customer_id": "CUST001",
        }
    ]

    result = customer_exists_by_id(customers, "cust001")

    assert result is True


def test_customer_exists_by_id_returns_false_when_customer_does_not_exist():
    customers = [
        {
            "customer_id": "CUST001",
        }
    ]

    result = customer_exists_by_id(customers, "CUST999")

    assert result is False


def test_email_exists_returns_true_when_email_exists():
    customers = [
        {
            "email": "ethan@example.com",
        }
    ]

    result = email_exists(customers, "  ETHAN@example.com  ")

    assert result is True


def test_email_exists_returns_false_when_email_does_not_exist():
    customers = [
        {
            "email": "ethan@example.com",
        }
    ]

    result = email_exists(customers, "other@example.com")

    assert result is False


def test_phone_number_exists_returns_true_when_phone_number_exists():
    customers = [
        {
            "phone_number": "+49123456789",
        }
    ]

    result = phone_number_exists(customers, "  +49123456789  ")

    assert result is True


def test_phone_number_exists_returns_false_when_phone_number_does_not_exist():
    customers = [
        {
            "phone_number": "+49123456789",
        }
    ]

    result = phone_number_exists(customers, "+49999999999")

    assert result is False


def test_build_customer_profile_returns_normalized_profile():
    result = build_customer_profile(
        customer_id="CUST001",
        first_name="  Ethan  ",
        surname="  Carter  ",
        year_of_birth=1990,
        month_of_birth=5,
        day_of_birth=12,
        postcode="  SW1A 1AA  ",
        first_line_of_address="  10 Downing Street  ",
        phone_number="  +49123456789  ",
        email="  ETHAN@example.com  ",
    )

    assert result == {
        "name": "Ethan Carter",
        "dob": "1990-05-12",
        "postcode": "SW1A 1AA",
        "first_line_address": "10 Downing Street",
        "phone_number": "+49123456789",
        "email": "ethan@example.com",
        "customer_id": "CUST001",
    }
