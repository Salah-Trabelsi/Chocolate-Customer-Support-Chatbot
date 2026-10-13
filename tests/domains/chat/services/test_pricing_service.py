import pytest

from app.domains.chat.services.pricing_service import (
    calculate_order_summary,
    convert_to_eur,
    format_price,
)


def test_format_price_chf():
    result = format_price(12.5, "CHF")

    assert result == "CHF 12.50"


def test_format_price_eur():
    result = format_price(12.5, "EUR")

    assert result == "12.50 €"


def test_format_price_unknown_currency():
    result = format_price(12.5, "USD")

    assert result == "12.50 USD"


def test_convert_to_eur_with_eur():
    result = convert_to_eur(10, "EUR")

    assert result == 10.0


def test_convert_to_eur_normalizes_currency():
    result = convert_to_eur(10, " eur ")

    assert result == 10.0


def test_convert_to_eur_with_chf():
    result = convert_to_eur(10, "CHF")

    assert isinstance(result, float)


def test_convert_to_eur_raises_error_for_unknown_currency():
    with pytest.raises(ValueError, match="No EUR exchange rate configured"):
        convert_to_eur(10, "ABC")


def test_calculate_order_summary_with_single_item():
    order = {
        "items": ["choco-001"],
        "quantity": [2],
    }

    inventory = [
        {
            "id": "choco-001",
            "name": "Dark Chocolate",
            "price": 5.5,
            "currency": "EUR",
        }
    ]

    result = calculate_order_summary(order, inventory)

    assert result["line_items"] == [
        {
            "item_id": "choco-001",
            "name": "Dark Chocolate",
            "quantity": 2,
            "price": 5.5,
            "currency": "EUR",
            "price_display": "5.50 €",
            "subtotal": 11.0,
            "subtotal_display": "11.00 €",
            "subtotal_in_eur": 11.0,
            "subtotal_in_eur_display": "11.00 €",
        }
    ]

    assert result["total_amounts"] == [
        {
            "currency": "EUR",
            "total": 11.0,
            "total_display": "11.00 €",
        }
    ]

    assert result["total_converted"]["currency"] == "EUR"
    assert result["total_converted"]["total"] == 11.0
    assert result["total_converted"]["total_display"] == "11.00 €"


def test_calculate_order_summary_with_multiple_items_same_currency():
    order = {
        "items": ["choco-001", "choco-002"],
        "quantity": [2, 3],
    }

    inventory = [
        {
            "id": "choco-001",
            "name": "Dark Chocolate",
            "price": 5.0,
            "currency": "EUR",
        },
        {
            "id": "choco-002",
            "name": "White Chocolate",
            "price": 4.0,
            "currency": "EUR",
        },
    ]

    result = calculate_order_summary(order, inventory)

    assert len(result["line_items"]) == 2

    assert result["total_amounts"] == [
        {
            "currency": "EUR",
            "total": 22.0,
            "total_display": "22.00 €",
        }
    ]

    assert result["total_converted"]["total"] == 22.0


def test_calculate_order_summary_with_unknown_product():
    order = {
        "items": ["missing-product"],
        "quantity": [2],
    }

    inventory = []

    result = calculate_order_summary(order, inventory)

    assert result["line_items"] == [
        {
            "item_id": "missing-product",
            "name": "Unknown product",
            "quantity": 2,
            "price": None,
            "currency": None,
            "subtotal": None,
            "subtotal_display": "Unknown",
            "subtotal_in_eur": None,
            "subtotal_in_eur_display": "Unknown",
        }
    ]

    assert result["total_amounts"] == []
    assert result["total_converted"]["total"] == 0.0
    assert result["total_converted"]["total_display"] == "0.00 €"


def test_calculate_order_summary_ignores_items_without_matching_quantity():
    order = {
        "items": ["choco-001", "choco-002"],
        "quantity": [2],
    }

    inventory = [
        {
            "id": "choco-001",
            "name": "Dark Chocolate",
            "price": 5.0,
            "currency": "EUR",
        },
        {
            "id": "choco-002",
            "name": "White Chocolate",
            "price": 4.0,
            "currency": "EUR",
        },
    ]

    result = calculate_order_summary(order, inventory)

    assert len(result["line_items"]) == 1
    assert result["line_items"][0]["item_id"] == "choco-001"
    assert result["total_converted"]["total"] == 10.0
