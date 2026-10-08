from datetime import datetime
from typing import List, Dict, Any
from app.domains.chat.seed_data import DEFAULT_CUSTOMERS
from app.domains.chat.repositories.json_repository import load_json_file, save_json_file
from app.domains.chat.services.pricing_service import calculate_order_summary

from langchain_core.tools import tool
from app.domains.chat.config import (
    CUSTOMERS_FILE_PATH,
    INVENTORY_FILE_PATH,
    ORDERS_FILE_PATH,
    PAYMENTS_FILE_PATH,
)
from app.domains.chat.vector_store import ChocolateShopVectorStore


vector_store = ChocolateShopVectorStore()

######## JSON DATABASE HELPERS ###########

def _load_inventory() -> List[Dict[str, Any]]:
    return load_json_file(
        file_path=INVENTORY_FILE_PATH,
        default_data=[],
    )


def _save_inventory(inventory: List[Dict[str, Any]]) -> None:
    save_json_file(
        file_path=INVENTORY_FILE_PATH,
        data=inventory,
    )


def _load_orders() -> List[Dict[str, Any]]:
    return load_json_file(
        file_path=ORDERS_FILE_PATH,
        default_data=[],
    )


def _save_orders(orders: List[Dict[str, Any]]) -> None:
    save_json_file(
        file_path=ORDERS_FILE_PATH,
        data=orders,
    )


def _load_customers() -> List[Dict[str, Any]]:
    return load_json_file(
        file_path=CUSTOMERS_FILE_PATH,
        default_data=DEFAULT_CUSTOMERS,
    )


def _save_customers(customers: List[Dict[str, Any]]) -> None:
    save_json_file(
        file_path=CUSTOMERS_FILE_PATH,
        data=customers,
    )


def _load_payments() -> List[Dict[str, Any]]:
    return load_json_file(
        file_path=PAYMENTS_FILE_PATH,
        default_data=[],
    )


def _save_payments(payments: List[Dict[str, Any]]) -> None:
    save_json_file(
        file_path=PAYMENTS_FILE_PATH,
        data=payments,
    )


######## ID HELPERS ###########

def _get_next_order_id(orders: List[Dict[str, Any]]) -> str:
    max_id = 0

    for order in orders:
        order_id = str(order.get("order_id", ""))

        if order_id.startswith("ORD"):
            try:
                number = int(order_id.replace("ORD", ""))
                max_id = max(max_id, number)
            except ValueError:
                continue

    return f"ORD{max_id + 1:03d}"


def _find_inventory_item(
    inventory: List[Dict[str, Any]],
    item_key: str,
) -> Dict[str, Any] | None:
    normalized_item_key = item_key.lower().strip()

    for item in inventory:
        if item["id"].lower().strip() == normalized_item_key:
            return item

        if item["name"].lower().strip() == normalized_item_key:
            return item

    return None




def _get_next_customer_id(customers: List[Dict[str, Any]]) -> str:
    """Generate the next customer ID based on the current customers."""

    max_id = 0

    for customer in customers:
        customer_id = customer.get("customer_id", "")

        if customer_id.startswith("CUST"):
            try:
                number = int(customer_id.replace("CUST", ""))
                max_id = max(max_id, number)
            except ValueError:
                continue
    
    return f"CUST{max_id + 1:03d}"




def _get_next_payment_id(payments: List[Dict[str, Any]]) -> str:
    max_id = 0

    for payment in payments:
        payment_id = str(payment.get("payment_id", ""))

        if payment_id.startswith("PAY"):
            try:
                number = int(payment_id.replace("PAY", ""))
                max_id = max(max_id, number)
            except ValueError:
                continue

    return f"PAY{max_id + 1:03d}"


    
@tool
def data_protection_check(
    name: str,
    postcode: str,
    year_of_birth: int,
    month_of_birth: int,
    day_of_birth: int,
):
    """
    Perform a data protection check against existing customers.

    Use this tool when the customer wants to retrieve account/profile details.
    The customer must provide full name, postcode, and date of birth.

    Args:
        name: Customer first and last name.
        postcode: Customer postcode.
        year_of_birth: Birth year.
        month_of_birth: Birth month.
        day_of_birth: Birth day.

    Returns:
        Customer details if the data protection check passes.
    """

    customers_database = _load_customers()

    requested_dob = f"{year_of_birth}-{month_of_birth:02}-{day_of_birth:02}"

    for customer in customers_database:
        if (
            customer["name"].lower().strip() == name.lower().strip()
            and customer["postcode"].lower().strip() == postcode.lower().strip()
            and customer["dob"] == requested_dob
        ):
            return {
                "status": "passed",
                "message": "DPA check passed.",
                "customer": customer,
            }

    return {
        "status": "failed",
        "message": "DPA check failed. No customer with these details was found.",
    }


@tool
def create_new_customer(first_name: str, surname: str, year_of_birth: int, month_of_birth: int, day_of_birth: int, postcode: str, first_line_of_address: str, phone_number: str, email: str) -> str:
    """
    Creates a customer profile, so that they can place orders.

    Args:
        first_name (str): Customers first name
        surname (str): Customers surname
        year_of_birth (int): Year customer was born
        month_of_birth (int): Month customer was born
        day_of_birth (int): Day customer was born
        postcode (str): Customer's postcode
        first_line_address (str): Customer's first line of address
        phone_number (str): Customer's phone number
        email (str): Customer's email address

    Returns:
        str: Confirmation that the profile has been created or any issues with the inputs
    """

    cleaned_phone_number = phone_number.replace(" ", "").strip()

    if not cleaned_phone_number.isdigit() or len(cleaned_phone_number) != 11:
        return "Invalid phone number. It should contain exactly 11 digits."

    customers_database = _load_customers()

    full_name = f"{first_name.strip()} {surname.strip()}"
    dob = f"{year_of_birth}-{month_of_birth:02}-{day_of_birth:02}"

    for customer in customers_database:
        if customer["email"].lower().strip() == email.lower().strip():
            return "A customer profile with this email already exists."

        if customer["phone_number"].strip() == cleaned_phone_number:
            return "A customer profile with this phone number already exists."

    customer_id = _get_next_customer_id(customers_database)

    new_customer = {
        "name": full_name,
        "dob": dob,
        "postcode": postcode.strip(),
        "first_line_address": first_line_of_address.strip(),
        "phone_number": cleaned_phone_number,
        "email": email.lower().strip(),
        "customer_id": customer_id,
    }

    customers_database.append(new_customer)
    _save_customers(customers_database)

    return f"Customer registered successfully with customer_id {customer_id}."



def _format_chroma_results(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert ChromaDB query result into a clean list for the LLM."""

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    formatted_results = []

    for document, metadata, distance in zip(documents, metadatas, distances):
        formatted_results.append({
            "matched_text": document,
            "metadata": metadata,
            "distance": distance,
        })

    return formatted_results


@tool
def query_knowledge_base(query: str) -> List[Dict[str, Any]]:
    """
    Search the chocolate shop FAQ knowledge base.

    Use this tool to answer customer questions about:
    orders, delivery, shipping, returns, damaged products, payments,
    subscriptions, gift messages, storage, allergens, and general shop policies.

    Args:
        query: Customer question to search in the FAQ knowledge base.

    Returns:
        A list of relevant FAQ question and answer pairs.
    """

    results = vector_store.query_faqs(query=query)
    return _format_chroma_results(results)


@tool
def search_for_product_recommendations(description: str) -> List[Dict[str, Any]]:
    """
    Search the chocolate inventory for product recommendations.

    Use this tool when the customer asks for chocolate products, for example:
    - dark Swiss chocolate
    - German milk chocolate
    - white chocolate with nuts
    - chocolate gifts
    - chocolate suitable for birthdays
    - affordable chocolate options
    - premium chocolate boxes

    Args:
        description: Description of the chocolate product the customer wants.

    Returns:
        A list of relevant chocolate products from the inventory with fresh price and quantity.
    """

    results = vector_store.query_inventories(query=description)
    formatted_results = _format_chroma_results(results)

    inventory_database = _load_inventory()
    products = []

    for result in formatted_results:
        metadata = result.get("metadata", {})
        product_id = metadata.get("id")

        fresh_product = next(
            (
                item
                for item in inventory_database
                if item["id"] == product_id
            ),
            None,
        )

        if fresh_product is None:
            continue

        products.append({
            "matched_text": result["matched_text"],
            "distance": result["distance"],
            "product": fresh_product,
        })

    return products


@tool
def filter_products_by_price(max_price: float, currency: str):
    """
    Filter chocolate products by maximum price and currency.

    Use this tool when the customer asks for products under a specific price, for example:
    - chocolates under 5 €
    - chocolates under 8 CHF
    - Swiss chocolate below 10 CHF
    - German chocolate under 4 EUR

    Args:
        max_price: Maximum product price.
        currency: Product currency. Use "CHF" for Swiss chocolate and "EUR" for German chocolate.

    Returns:
        Matching products with price less than or equal to max_price.
    """

    normalized_currency = currency.upper().strip()

    if normalized_currency in ["€", "EURO", "EUROS"]:
        normalized_currency = "EUR"

    if normalized_currency in ["CHF", "FRANC", "FRANCS", "SWISS FRANC"]:
        normalized_currency = "CHF"

    results = vector_store.filter_products_by_price(
        max_price=max_price,
        currency=normalized_currency,
    )

    products = []

    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    for document, metadata in zip(documents, metadatas):
        products.append({
            "matched_text": document,
            "metadata": metadata,
        })

    return products



@tool
def retrieve_existing_customer_orders(customer_id: str) -> List[Dict[str, Any]] | str:
    """
    Retrieve existing orders for a customer.

    Args:
        customer_id: Customer unique ID.

    Returns:
        List of orders associated with the customer.
    """

    orders_database = _load_orders()

    customer_orders = [
        order for order in orders_database
        if order["customer_id"] == customer_id
    ]

    if not customer_orders:
        return f"No orders associated with this customer id: {customer_id}"

    return customer_orders



@tool
def place_order(items: Dict[str, int], customer_id: str) -> Dict[str, Any] | str:
    """
    Place an order for the requested chocolate products.

    Use this tool only after the customer has a customer profile.

    Args:
        items: Dictionary of products to order.
               The key can be the product id, for example "ch021",
               or the exact product name, for example "Swiss Dark Chocolate Orange Bar".
               The value is the quantity.
        customer_id: Customer ID, for example "CUST003".

    Returns:
        Structured order confirmation with order details, totals, and status.
    """

    customers_database = _load_customers()
    inventory_database = _load_inventory()
    orders_database = _load_orders()

    customer_exists = any(
        customer["customer_id"] == customer_id
        for customer in customers_database
    )

    if not customer_exists:
        return f"Order cannot be placed. Customer ID {customer_id} was not found."

    availability_messages = []
    resolved_items = {}

    for item_key, quantity in items.items():
        if quantity <= 0:
            availability_messages.append(
                f"Invalid quantity for {item_key}. Quantity must be greater than 0."
            )
            continue

        inventory_item = _find_inventory_item(
            inventory=inventory_database,
            item_key=item_key,
        )

        if inventory_item is None:
            availability_messages.append(
                f"Item '{item_key}' was not found in the inventory."
            )
            continue

        if quantity > inventory_item["quantity"]:
            availability_messages.append(
                f"Insufficient quantity for {inventory_item['name']}.\n"
                f"Available: {inventory_item['quantity']}\n"
                f"Requested: {quantity}"
            )
            continue

        resolved_items[inventory_item["id"]] = {
            "name": inventory_item["name"],
            "quantity": quantity,
        }

    if availability_messages:
        return (
            "Order cannot be placed due to the following issues:\n"
            + "\n".join(availability_messages)
        )

    order_id = _get_next_order_id(orders_database)

    new_order = {
        "order_id": order_id,
        "customer_id": customer_id,
        "status": "Waiting for payment",
        "items": list(resolved_items.keys()),
        "item_names": [item["name"] for item in resolved_items.values()],
        "quantity": [item["quantity"] for item in resolved_items.values()],
    }

    orders_database.append(new_order)

    for item_id, item_data in resolved_items.items():
        for inventory_item in inventory_database:
            if inventory_item["id"] == item_id:
                inventory_item["quantity"] -= item_data["quantity"]

    _save_orders(orders_database)
    _save_inventory(inventory_database)

    order_summary = calculate_order_summary(
        order=new_order,
        inventory=inventory_database,
    )

    return {
        "status": "order_placed",
        "message": f"Order {order_id} has been placed successfully.",
        "order": {
            "order_id": order_id,
            "customer_id": customer_id,
            "status": "Waiting for payment",
            "items": [
                {
                    "item_id": item_id,
                    "name": item_data["name"],
                    "quantity": item_data["quantity"],
                }
                for item_id, item_data in resolved_items.items()
            ],
            "line_items": order_summary["line_items"],
            "total_amounts": order_summary["total_amounts"],
            "total_converted": order_summary.get("total_converted"),
        },
    }


def _verify_customer_and_order_data(
    name: str,
    postcode: str,
    year_of_birth: int,
    month_of_birth: int,
    day_of_birth: int,
    order_id: str,
) -> Dict[str, Any]:
    customers_database = _load_customers()
    orders_database = _load_orders()
    inventory_database = _load_inventory()

    requested_dob = f"{year_of_birth}-{month_of_birth:02}-{day_of_birth:02}"
    normalized_order_id = order_id.upper().strip()

    customer = next(
        (
            customer
            for customer in customers_database
            if customer["name"].lower().strip() == name.lower().strip()
            and customer["postcode"].lower().strip() == postcode.lower().strip()
            and customer["dob"] == requested_dob
        ),
        None,
    )

    if customer is None:
        return {
            "status": "dpa_failed",
            "message": "DPA check failed. No customer with these details was found.",
        }

    order = next(
        (
            order
            for order in orders_database
            if order["order_id"].upper().strip() == normalized_order_id
        ),
        None,
    )

    if order is None:
        return {
            "status": "order_not_found",
            "message": f"Order {normalized_order_id} was not found.",
            "customer": {
                "customer_id": customer["customer_id"],
                "name": customer["name"],
            },
        }

    if order["customer_id"].upper().strip() != customer["customer_id"].upper().strip():
        return {
            "status": "forbidden",
            "message": f"Order {normalized_order_id} does not belong to {customer['name']}.",
            "customer": {
                "customer_id": customer["customer_id"],
                "name": customer["name"],
            },
            "order_customer_id": order["customer_id"],
        }

    order_summary = calculate_order_summary(
        order=order,
        inventory=inventory_database,
    )

    return {
        "status": "verified",
        "message": "Customer and order verified successfully.",
        "customer": customer,
        "order": order,
        "order_summary": order_summary,
    }


@tool
def verify_customer_and_order(
    name: str,
    postcode: str,
    year_of_birth: int,
    month_of_birth: int,
    day_of_birth: int,
    order_id: str,
) -> Dict[str, Any]:
    """
    Verify a customer with DPA details and retrieve their order.

    Use this tool when the customer wants to pay for an order or view a specific order.
    """

    verification = _verify_customer_and_order_data(
        name=name,
        postcode=postcode,
        year_of_birth=year_of_birth,
        month_of_birth=month_of_birth,
        day_of_birth=day_of_birth,
        order_id=order_id,
    )

    if verification["status"] != "verified":
        return verification

    customer = verification["customer"]
    order = verification["order"]
    order_summary = verification["order_summary"]

    return {
        "status": "verified",
        "message": "Customer and order verified successfully.",
        "customer": {
            "customer_id": customer["customer_id"],
            "name": customer["name"],
            "postcode": customer["postcode"],
            "email": customer["email"],
        },
        "order": {
            "order_id": order["order_id"],
            "customer_id": order["customer_id"],
            "status": order["status"],
            "line_items": order_summary["line_items"],
            "total_amounts": order_summary["total_amounts"],
            "total_converted": order_summary["total_converted"],
        },
    }


@tool
def process_payment(
    name: str,
    postcode: str,
    year_of_birth: int,
    month_of_birth: int,
    day_of_birth: int,
    order_id: str,
    payment_method: str = "test_card",
) -> Dict[str, Any]:
    """
    Process a fake payment for an order.

    Use this tool only after:
    - verify_customer_and_order returned status "verified"
    - the customer confirmed they want to proceed with payment

    This tool re-verifies the customer and order before processing payment.

    Args:
        name: Customer full name.
        postcode: Customer postcode.
        year_of_birth: Birth year.
        month_of_birth: Birth month.
        day_of_birth: Birth day.
        order_id: Order ID, for example "ORD003".
        payment_method: Fake payment method, for example "test_card", "paypal", "apple_pay", or "google_pay".

    Returns:
        Payment confirmation and updated order status.
    """

    verification = _verify_customer_and_order_data(
        name=name,
        postcode=postcode,
        year_of_birth=year_of_birth,
        month_of_birth=month_of_birth,
        day_of_birth=day_of_birth,
        order_id=order_id,
    )

    if verification["status"] != "verified":
        return verification

    orders_database = _load_orders()
    payments_database = _load_payments()

    customer = verification["customer"]
    verified_order = verification["order"]
    order_summary = verification["order_summary"]

    normalized_order_id = verified_order["order_id"].upper().strip()

    order = next(
        (
            order
            for order in orders_database
            if order["order_id"].upper().strip() == normalized_order_id
        ),
        None,
    )

    if order is None:
        return {
            "status": "order_not_found",
            "message": f"Order {normalized_order_id} was not found.",
        }

    if order["status"] == "Paid":
        return {
            "status": "already_paid",
            "message": f"Order {normalized_order_id} has already been paid.",
            "order": order,
        }

    if order["status"] != "Waiting for payment":
        return {
            "status": "invalid_status",
            "message": (
                f"Order {normalized_order_id} cannot be paid because its current "
                f"status is '{order['status']}'."
            ),
        }

    payment_id = _get_next_payment_id(payments_database)

    new_payment = {
        "payment_id": payment_id,
        "order_id": normalized_order_id,
        "customer_id": customer["customer_id"],
        "status": "Paid",
        "payment_method": payment_method,
        "amounts": order_summary["total_amounts"],
        "total_converted": order_summary["total_converted"],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    payments_database.append(new_payment)

    order["status"] = "Paid"
    order["payment_id"] = payment_id

    _save_orders(orders_database)
    _save_payments(payments_database)

    return {
        "status": "paid",
        "message": f"Payment {payment_id} processed successfully for order {normalized_order_id}.",
        "customer": {
            "customer_id": customer["customer_id"],
            "name": customer["name"],
        },
        "payment": new_payment,
        "order": order,
    }
