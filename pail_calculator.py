from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Iterable

PAIL_CAPACITY_KG = Decimal("15")


@dataclass(frozen=True)
class PailResult:
    quantity_kg: Decimal
    equivalent_pails: Decimal
    whole_pails: int


def parse_quantity(value: str | int | float | Decimal) -> Decimal:
    if isinstance(value, Decimal):
        quantity = value
    else:
        normalized = str(value).strip().replace(",", ".")
        if not normalized:
            raise ValueError("Jumlah kg belum diisi.")
        try:
            quantity = Decimal(normalized)
        except InvalidOperation as exc:
            raise ValueError("Jumlah harus berupa angka, misalnya 12,5.") from exc

    if not quantity.is_finite():
        raise ValueError("Jumlah harus berupa angka yang valid.")
    if quantity < 0:
        raise ValueError("Jumlah tidak boleh negatif.")
    return quantity


def calculate_pails(quantity_kg: str | int | float | Decimal) -> PailResult:
    quantity = parse_quantity(quantity_kg)
    equivalent = quantity / PAIL_CAPACITY_KG
    whole = int(equivalent.to_integral_value(rounding=ROUND_HALF_UP))
    return PailResult(quantity, equivalent, whole)


def calculate_total(quantities_kg: Iterable[str | int | float | Decimal]) -> PailResult:
    total = sum((parse_quantity(value) for value in quantities_kg), Decimal("0"))
    return calculate_pails(total)
