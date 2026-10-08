from typing import Any, Dict, List


def find_customer_by_dpa(
    customers: List[Dict[str, Any]],
    name: str,
    postcode: str,
    year_of_birth: int,
    month_of_birth: int,
    day_of_birth: int,
) -> Dict[str, Any] | None:
    requested_dob = f"{year_of_birth}-{month_of_birth:02}-{day_of_birth:02}"

    return next(
        (
            customer
            for customer in customers
            if customer["name"].lower().strip() == name.lower().strip()
            and customer["postcode"].lower().strip() == postcode.lower().strip()
            and customer["dob"] == requested_dob
        ),
        None,
    )


def customer_exists_by_id(
    customers: List[Dict[str, Any]],
    customer_id: str,
) -> bool:
    return any(
        customer["customer_id"].upper().strip() == customer_id.upper().strip()
        for customer in customers
    )


def email_exists(
    customers: List[Dict[str, Any]],
    email: str,
) -> bool:
    return any(
        customer["email"].lower().strip() == email.lower().strip()
        for customer in customers
    )


def phone_number_exists(
    customers: List[Dict[str, Any]],
    phone_number: str,
) -> bool:
    return any(
        customer["phone_number"].strip() == phone_number.strip()
        for customer in customers
    )


def build_customer_profile(
    customer_id: str,
    first_name: str,
    surname: str,
    year_of_birth: int,
    month_of_birth: int,
    day_of_birth: int,
    postcode: str,
    first_line_of_address: str,
    phone_number: str,
    email: str,
) -> Dict[str, Any]:
    full_name = f"{first_name.strip()} {surname.strip()}"
    dob = f"{year_of_birth}-{month_of_birth:02}-{day_of_birth:02}"

    return {
        "name": full_name,
        "dob": dob,
        "postcode": postcode.strip(),
        "first_line_address": first_line_of_address.strip(),
        "phone_number": phone_number.strip(),
        "email": email.lower().strip(),
        "customer_id": customer_id,
    }