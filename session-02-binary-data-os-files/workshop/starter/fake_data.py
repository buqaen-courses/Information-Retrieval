"""Stdlib-only fake profile generator for Session 2.

Uses only `random` with a fixed seed, so 10 000 profiles are identical
on every machine. No external dependencies.
"""
from __future__ import annotations

import random

FIRST_NAMES = [
    "Alice", "Bob", "Carol", "David", "Eve", "Frank", "Grace", "Heidi",
    "Ivan", "Judy", "Karl", "Liam", "Mona", "Nina", "Oscar", "Pat",
    "Quinn", "Rita", "Sam", "Tina", "Umar", "Vera", "Will", "Xena",
    "Yusuf", "Zara",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
]

DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "proton.me", "example.org"]

STREETS = ["Oak", "Maple", "Cedar", "Pine", "Elm", "Birch", "Walnut", "Cherry"]
STREET_TYPES = ["St", "Ave", "Blvd", "Ln", "Dr", "Way"]

CITIES = [
    "Springfield", "Riverton", "Lakeside", "Hill Valley", "Maplewood",
    "Cedar Falls", "Brookside", "Fairview", "Greenville", "Bayside",
]

STATES = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]

PRODUCTS = [
    "laptop stand", "usb hub", "wireless charger", "desk lamp", "webcam",
    "keyboard", "mouse pad", "monitor arm", "headphone stand", "cable organizer",
]

FREE_TAGS = ["new", "sale", "bestseller", "limited", "eco", "premium"]


def generate_profiles(n: int, seed: int = 42) -> list[dict[str, object]]:
    """Generate n fake user profiles deterministically.

    Each profile has: id, name, email, age, price, city, state, zip,
    street, product, tags. Uses only stdlib random with a fixed seed.
    """
    """Generate n fake user profiles deterministically."""
    rng = random.Random(seed)
    profiles: list[dict[str, object]] = []
    for i in range(n):
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        domain = rng.choice(DOMAINS)
        street_num = rng.randint(1, 9999)
        street = rng.choice(STREETS)
        street_type = rng.choice(STREET_TYPES)
        city = rng.choice(CITIES)
        state = rng.choice(STATES)
        zip_code = rng.randint(10000, 99999)
        product = rng.choice(PRODUCTS)
        price = round(rng.uniform(5.0, 500.0), 2)
        tags = rng.sample(FREE_TAGS, k=rng.randint(0, 3))
        email = (first + "." + last + "@" + domain).lower()
        profiles.append({
            "id": "u-%05d" % (i + 1),
            "name": first + " " + last,
            "email": email,
            "age": rng.randint(18, 75),
            "price": price,
            "city": city,
            "state": state,
            "zip": zip_code,
            "street": "%d %s %s" % (street_num, street, street_type),
            "product": product,
            "tags": tags,
        })
    return profiles
