"""
Collection Noir — static site builder

Reads every JSON file in data/products/, renders it through
templates/product-page.html, and writes the result to
public/products/{slug}/index.html.

Usage:
    python3 build/build.py
"""
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
DATA_PRODUCTS = ROOT / "data" / "products"
DATA_STONES = ROOT / "data" / "stones.json"
TEMPLATES = ROOT / "templates"
PUBLIC = ROOT / "public"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build():
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)))
    template = env.get_template("product-page.html")
    stones = load_json(DATA_STONES)

    product_files = sorted(DATA_PRODUCTS.glob("*.json"))
    if not product_files:
        print("No product data files found in", DATA_PRODUCTS)
        return

    for product_file in product_files:
        product = load_json(product_file)
        html = template.render(product=product, stones=stones)

        out_dir = PUBLIC / "products" / product["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "index.html"
        out_path.write_text(html, encoding="utf-8")

        print(f"Built {product['slug']:<25} -> {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
