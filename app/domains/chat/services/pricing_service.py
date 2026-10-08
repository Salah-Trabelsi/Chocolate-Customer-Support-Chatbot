from typing import Any, Dict, List

from app.domains.chat.config import BASE_CURRENCY, EXCHANGE_RATES_TO_EUR


def format_price(amount: float, currency: str) -> str:
    """Format the price with the appropriate currency symbol."""

    if currency == "CHF":
        return f"CHF {amount:.2f}"

    if currency == "EUR":
        return f"{amount:.2f} €"

    return f"{amount:.2f} {currency}"


def convert_to_eur(amount: float, currency: str) -> float:
    """Convert an amount to EUR using static demo exchange rates."""

    normalized_currency = currency.upper().strip()
    exchange_rate = EXCHANGE_RATES_TO_EUR.get(normalized_currency)

    if exchange_rate is None:
        raise ValueError(f"No EUR exchange rate configured for currency: {currency}")

    return round(amount * exchange_rate, 2)


def calculate_order_summary(
    order: Dict[str, Any],
    inventory: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Calculate the order summary including totals by currency and final EUR total."""

    line_items = []
    totals_by_currency = {}
    total_in_eur = 0.0

    order_items = order.get("items", [])
    quantities = order.get("quantity", [])

    for item_id, quantity in zip(order_items, quantities):
        inventory_item = next(
            (item for item in inventory if item["id"] == item_id),
            None,
        )

        if inventory_item is None:
            line_items.append({
                "item_id": item_id,
                "name": "Unknown product",
                "quantity": quantity,
                "price": None,
                "currency": None,
                "subtotal": None,
                "subtotal_display": "Unknown",
                "subtotal_in_eur": None,
                "subtotal_in_eur_display": "Unknown",
            })
            continue

        price = float(inventory_item["price"])
        currency = inventory_item["currency"]
        subtotal = round(price * quantity, 2)
        subtotal_in_eur = convert_to_eur(subtotal, currency)

        totals_by_currency[currency] = round(
            totals_by_currency.get(currency, 0) + subtotal,
            2,
        )

        total_in_eur = round(total_in_eur + subtotal_in_eur, 2)

        line_items.append({
            "item_id": inventory_item["id"],
            "name": inventory_item["name"],
            "quantity": quantity,
            "price": price,
            "currency": currency,
            "price_display": format_price(price, currency),
            "subtotal": subtotal,
            "subtotal_display": format_price(subtotal, currency),
            "subtotal_in_eur": subtotal_in_eur,
            "subtotal_in_eur_display": format_price(subtotal_in_eur, "EUR"),
        })

    total_amounts = [
        {
            "currency": currency,
            "total": amount,
            "total_display": format_price(amount, currency),
        }
        for currency, amount in totals_by_currency.items()
    ]

    return {
        "line_items": line_items,
        "total_amounts": total_amounts,
        "total_converted": {
            "currency": BASE_CURRENCY,
            "total": total_in_eur,
            "total_display": format_price(total_in_eur, BASE_CURRENCY),
            "exchange_rates": EXCHANGE_RATES_TO_EUR,
        },
    }