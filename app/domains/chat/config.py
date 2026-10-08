from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CUSTOMERS_FILE_PATH = PROJECT_ROOT / "customers_database.json"
INVENTORY_FILE_PATH = PROJECT_ROOT / "inventory.json"
ORDERS_FILE_PATH = PROJECT_ROOT / "orders_database.json"
PAYMENTS_FILE_PATH = PROJECT_ROOT / "payments_database.json"

BASE_CURRENCY = "EUR"

EXCHANGE_RATES_TO_EUR = {
    "EUR": 1.0,
    "CHF": 1.09,
}