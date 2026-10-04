from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal, ROUND_FLOOR

from pail_calculator import PAIL_CAPACITY_KG, parse_quantity


def build_printout(product_name: str, materials: Iterable[tuple[str, str]]) -> str:
    product = product_name.strip()
    lines: list[str] = []
    if product:
        lines.extend((product[0].upper() + product[1:] + ":", ""))

    for name, quantity_text in materials:
        material = name.strip()
        quantity = quantity_text.strip()
        if not material or not quantity:
            continue
        try:
            parse_quantity(quantity)
        except ValueError:
            continue
        display_quantity = quantity.replace(".", ",")
        display_material = material[0].upper() + material[1:]
        lines.append(f"{display_material} {display_quantity}")

    return "\n".join(lines).rstrip()


def build_pail_printout(product_name: str, materials: Iterable[tuple[str, str]]) -> str:
    product = product_name.strip()
    lines: list[str] = []
    if product:
        lines.extend((product + ":", ""))

    for name, quantity_text in materials:
        material = name.strip()
        quantity_text = quantity_text.strip()
        if not material or not quantity_text:
            continue
        try:
            quantity = parse_quantity(quantity_text)
        except ValueError:
            continue

        if quantity == 0:
            pail_count = 0
        elif quantity < PAIL_CAPACITY_KG:
            pail_count = 1
        else:
            pail_count = int((quantity / PAIL_CAPACITY_KG).to_integral_value(rounding=ROUND_FLOOR))
        lines.append(f"{material} {pail_count} pail")

    return "\n".join(lines).rstrip()
