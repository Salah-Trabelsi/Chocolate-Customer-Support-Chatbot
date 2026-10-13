from app.domains.chat.services.id_service import (
    get_next_customer_id,
    get_next_order_id,
    get_next_payment_id,
)


def test_get_next_order_id_returns_first_id_when_orders_empty():
    result = get_next_order_id([])

    assert result == "ORD001"


def test_get_next_order_id_returns_next_id():
    orders = [
        {"order_id": "ORD001"},
        {"order_id": "ORD002"},
        {"order_id": "ORD010"},
    ]

    result = get_next_order_id(orders)

    assert result == "ORD011"


def test_get_next_order_id_ignores_invalid_ids():
    orders = [
        {"order_id": "ORD001"},
        {"order_id": "INVALID"},
        {"order_id": "ORDABC"},
        {"order_id": ""},
        {},
    ]

    result = get_next_order_id(orders)

    assert result == "ORD002"


def test_get_next_customer_id_returns_first_id_when_customers_empty():
    result = get_next_customer_id([])

    assert result == "CUST001"


def test_get_next_customer_id_returns_next_id():
    customers = [
        {"customer_id": "CUST001"},
        {"customer_id": "CUST002"},
        {"customer_id": "CUST010"},
    ]

    result = get_next_customer_id(customers)

    assert result == "CUST011"


def test_get_next_customer_id_ignores_invalid_ids():
    customers = [
        {"customer_id": "CUST001"},
        {"customer_id": "INVALID"},
        {"customer_id": "CUSTABC"},
        {"customer_id": ""},
        {},
    ]

    result = get_next_customer_id(customers)

    assert result == "CUST002"


def test_get_next_payment_id_returns_first_id_when_payments_empty():
    result = get_next_payment_id([])

    assert result == "PAY001"


def test_get_next_payment_id_returns_next_id():
    payments = [
        {"payment_id": "PAY001"},
        {"payment_id": "PAY002"},
        {"payment_id": "PAY010"},
    ]

    result = get_next_payment_id(payments)

    assert result == "PAY011"


def test_get_next_payment_id_ignores_invalid_ids():
    payments = [
        {"payment_id": "PAY001"},
        {"payment_id": "INVALID"},
        {"payment_id": "PAYABC"},
        {"payment_id": ""},
        {},
    ]

    result = get_next_payment_id(payments)

    assert result == "PAY002"
