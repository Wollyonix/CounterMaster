from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path
from collections.abc import Iterable
from contextlib import closing


def database_path() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        data_dir = Path(local_app_data) / "DmasterCounter"
    else:
        data_dir = Path.home() / ".dmastercounter"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "itemlist.db"


class ItemDatabase:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else database_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """CREATE TABLE IF NOT EXISTS items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        kind TEXT NOT NULL CHECK(kind IN ('product', 'material')),
                        name TEXT NOT NULL COLLATE NOCASE,
                        UNIQUE(kind, name)
                    )"""
                )

    def list_items(self, kind: str) -> list[tuple[int, str]]:
        self._validate_kind(kind)
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT id, name FROM items WHERE kind = ? ORDER BY name COLLATE NOCASE", (kind,)
            ).fetchall()
        return [(int(item_id), str(name)) for item_id, name in rows]

    def add_item(self, kind: str, name: str) -> bool:
        self._validate_kind(kind)
        normalized = " ".join(name.strip().split())
        if not normalized:
            raise ValueError("Nama item tidak boleh kosong.")
        try:
            with closing(self._connect()) as connection:
                with connection:
                    connection.execute("INSERT INTO items(kind, name) VALUES (?, ?)", (kind, normalized))
        except sqlite3.IntegrityError:
            return False
        return True

    def delete_item(self, item_id: int) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.execute("DELETE FROM items WHERE id = ?", (item_id,))

    @staticmethod
    def _validate_kind(kind: str) -> None:
        if kind not in {"product", "material"}:
            raise ValueError("Jenis item tidak dikenal.")


def _normalize_search(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.casefold())


def _matches_name(query: str, name: str) -> bool:
    query_parts = _normalize_search(query)
    if not query_parts:
        return False
    name_parts = _normalize_search(name)
    if not name_parts:
        return False

    original_parts = re.findall(r"[a-z0-9]+", name.casefold())
    acronym_parts = []
    for original, normalized in zip(re.findall(r"[A-Za-z0-9]+", name), original_parts):
        acronym_parts.append(original.casefold() if len(original) > 1 and original.isupper() else normalized[0])
    acronym = "".join(acronym_parts)
    if len(query_parts) == 1 and len(query_parts[0]) > 1 and query_parts[0] in acronym:
        return True
    return all(any(part in name_part for name_part in name_parts) for part in query_parts)


def search_items(items: Iterable[tuple[int, str]], query: str) -> list[tuple[int, str]]:
    return [(item_id, name) for item_id, name in items if _matches_name(query, name)]


def search_product_names(
    products: Iterable[tuple[int, str]],
    materials: Iterable[tuple[int, str]],
    query: str,
) -> list[tuple[int, str]]:
    product_matches = search_items(products, query)
    material_matches = search_items(materials, query)
    matches: list[tuple[int, str]] = []
    seen_names: set[str] = set()
    for item_id, name in (*product_matches, *material_matches):
        normalized = " ".join(name.casefold().split())
        if normalized not in seen_names:
            seen_names.add(normalized)
            matches.append((item_id, name))
    return matches
