from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from pail_calculator import parse_quantity


@dataclass(frozen=True)
class FormulationLineResult:
    reference_grams: Decimal
    percentage: Decimal
    quantity_kg: Decimal


def calculate_formulation(
    gramasi_values: Iterable[str | int | float | Decimal],
    target_total_kg: str | int | float | Decimal,
) -> tuple[list[FormulationLineResult], Decimal]:
    values = [parse_quantity(value) for value in gramasi_values]
    if not values:
        raise ValueError("Masukkan setidaknya satu gramasi bahan.")
    if any(value <= 0 for value in values):
        raise ValueError("Gramasi setiap bahan harus lebih besar dari 0.")

    target = parse_quantity(target_total_kg)
    if target <= 0:
        raise ValueError("Total produksi harus lebih besar dari 0 kg.")

    gramasi_sum = sum(values, Decimal("0"))
    rows = [
        FormulationLineResult(
            reference_grams=value,
            percentage=value / gramasi_sum * Decimal("100"),
            quantity_kg=target * value / gramasi_sum,
        )
        for value in values
    ]
    return rows, gramasi_sum
