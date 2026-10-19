"""Persistance JSON centralisée pour Atelier PVC Pro."""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import date
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = PROJECT_DIR / "storage"
DB_PATH = STORAGE_DIR / "data.json"
TABLES = ("clients", "products", "quotes", "jobs", "invoices", "payments")


def _empty_db() -> dict[str, list[dict[str, Any]]]:
    return {table: [] for table in TABLES}


def initialize_db() -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        save_db(_empty_db())


def load_db() -> dict[str, list[dict[str, Any]]]:
    initialize_db()
    try:
        with DB_PATH.open("r", encoding="utf-8") as file:
            db = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            "La base storage/data.json est illisible. Restaure une sauvegarde JSON valide."
        ) from exc

    if not isinstance(db, dict):
        raise ValueError("La base JSON doit être un objet contenant les tables de l'application.")
    for table in TABLES:
        if table not in db:
            db[table] = []
        if not isinstance(db[table], list):
            raise ValueError(f"La section '{table}' doit être une liste.")
    return db


def save_db(db: dict[str, list[dict[str, Any]]]) -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    for table in TABLES:
        if table not in db or not isinstance(db[table], list):
            raise ValueError(f"La base est invalide : section '{table}' absente ou incorrecte.")

    temp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=STORAGE_DIR,
            suffix=".tmp", delete=False
        ) as file:
            temp_path = file.name
            json.dump(db, file, ensure_ascii=False, indent=2)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp_path, DB_PATH)
    except OSError as exc:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        raise RuntimeError("Impossible d'enregistrer la base JSON.") from exc


def new_id() -> str:
    return str(uuid.uuid4())


def today() -> str:
    return date.today().isoformat()


def create_record(table: str, record: dict[str, Any]) -> dict[str, Any]:
    if table not in TABLES:
        raise ValueError("Table inconnue.")
    db = load_db()
    new_record = dict(record)
    new_record.setdefault("id", new_id())
    new_record.setdefault("created_at", today())
    db[table].append(new_record)
    save_db(db)
    return new_record


def update_record(table: str, record_id: str, updates: dict[str, Any]) -> dict[str, Any]:
    if table not in TABLES:
        raise ValueError("Table inconnue.")
    db = load_db()
    for record in db[table]:
        if record.get("id") == record_id:
            record.update(updates)
            save_db(db)
            return record
    raise ValueError("Enregistrement introuvable.")


def delete_record(table: str, record_id: str) -> None:
    if table not in TABLES:
        raise ValueError("Table inconnue.")
    db = load_db()
    original_count = len(db[table])
    db[table] = [record for record in db[table] if record.get("id") != record_id]
    if len(db[table]) == original_count:
        raise ValueError("Enregistrement introuvable.")
    save_db(db)


def restore_db(db: dict[str, Any]) -> None:
    if not isinstance(db, dict):
        raise ValueError("Le fichier de sauvegarde doit contenir un objet JSON.")
    clean = _empty_db()
    for table in TABLES:
        value = db.get(table, [])
        if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
            raise ValueError(f"La section '{table}' de la sauvegarde est invalide.")
        clean[table] = value
    save_db(clean)
