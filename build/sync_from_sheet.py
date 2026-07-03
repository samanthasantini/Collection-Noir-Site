"""
Collection Noir — Sheet -> JSON sync

Reads the product master CSV (exported from the live Google Sheet) and
writes/updates one JSON file per product in data/products/, in exactly
the schema the existing site build.py already expects.

This is the ONLY step that touches data/products/*.json. Nobody edits
those JSON files by hand anymore — the sheet is the source of truth.

Usage:
    python3 build/sync_from_sheet.py [path_to_csv]

Defaults to data/products_master.csv if no path is given.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = ROOT / "data" / "products_master.csv"
PRODUCTS_DIR = ROOT / "data" / "products"


def parse_stones(row):
    stones = []
    for key in ("stone_1", "stone_2", "stone_3"):
        val = (row.get(key) or "").strip()
        if val:
            stones.append(val)
    return stones


def row_to_product(row):
    price = (row.get("price") or "").strip()
    return {
        "slug": row["slug"].strip(),
        "name": row["name"].strip(),
        "category": row.get("category", "").strip(),
        "price": price if price else None,
        "short_description": row.get("short_description", "").strip(),
        "stones": parse_stones(row),
        "lead_time_weeks": row.get("lead_time_weeks", "").strip(),
        "dimensions": row.get("dimensions", "").strip(),
        "primary_image_filename": row.get("primary_image_filename", "").strip(),
        "spec_sheet_filename": row.get("spec_sheet_filename", "").strip(),
        "status": row.get("status", "draft").strip(),
    }


def sync(csv_path: Path):
    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        sys.exit(1)

    PRODUCTS_DIR.mkdir(parents=True, exist_ok=True)

    written = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("slug", "").strip():
                continue
            product = row_to_product(row)
            out_path = PRODUCTS_DIR / f"{product['slug']}.json"
            with open(out_path, "w", encoding="utf-8") as out:
                json.dump(product, out, indent=2, ensure_ascii=False)
            written.append(product["slug"])

    print(f"Synced {len(written)} products from {csv_path.name}:")
    for slug in written:
        print(f"  - {slug}")


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    sync(csv_path)
