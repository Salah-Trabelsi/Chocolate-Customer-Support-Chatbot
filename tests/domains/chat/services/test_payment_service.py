from datetime import datetime

from app.domains.chat.services.payment_service import (
    build_payment,
    is_order_already_paid,
    is_order_waiting_for_payment,
    mark_order_as_paid,
)


def test_is_order_already_paid_returns_true_for_paid_order():
    order = {
        "status": "Paid",
    }

    result = is_order_already_paid(order)

    assert result is True


def test_is_order_already_paid_returns_false_for_unpaid_order():
    order = {
        "status": "Waiting for payment",
    }

    result = is_order_already_paid(order)

    assert result is False


def test_is_order_waiting_for_payment_returns_true():
    order = {
        "status": "Waiting for payment",
    }

    result = is_order_waiting_for_payment(order)

    assert result is True


def test_is_order_waiting_for_payment_returns_false_for_paid_order():
    order = {
        "status": "Paid",
    }

    result = is_order_waiting_for_payment(order)

    assert result is False


def test_mark_order_as_paid_updates_order_status_and_payment_id():
    order = {
        "order_id": "ORD001",
        "status": "Waiting for payment",
    }

    result = mark_order_as_paid(order, "PAY001")

    assert result == {
        "order_id": "ORD001",
        "status": "Paid",
        "payment_id": "PAY001",
    }


def test_mark_order_as_paid_mutates_and_returns_same_order():
    order = {
        "order_id": "ORD001",
        "status": "Waiting for payment",
    }

    result = mark_order_as_paid(order, "PAY001")

    assert result is order


def test_build_payment_returns_payment_data():
    order_summary = {
        "total_amounts": [
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

    result = build_payment(
        payment_id="PAY001",
        order_id="ORD001",
        customer_id="CUST001",
        payment_method="Credit card",
        order_summary=order_summary,
    )

    assert result["payment_id"] == "PAY001"
    assert result["order_id"] == "ORD001"
    assert result["customer_id"] == "CUST001"
    assert result["status"] == "Paid"
    assert result["payment_method"] == "Credit card"
    assert result["amounts"] == order_summary["total_amounts"]
    assert result["total_converted"] == order_summary["total_converted"]


def test_build_payment_created_at_is_iso_datetime():
    order_summary = {
        "total_amounts": [],
        "total_converted": {
            "currency": "EUR",
            "total": 0.0,
            "total_display": "0.00 €",
        },
    }

    result = build_payment(
        payment_id="PAY001",
        order_id="ORD001",
        customer_id="CUST001",
        payment_method="PayPal",
        order_summary=order_summary,
    )

    parsed_datetime = datetime.fromisoformat(result["created_at"])

    assert isinstance(parsed_datetime, datetime)
