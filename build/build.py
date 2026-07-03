"""
Collection Noir — static site builder

Reads every JSON file in data/products/, renders it through
templates/product-page.html, and writes the result to
public/products/{slug}/index.html.

Usage:
    python3 build/build.py
"""
import json
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
DATA_PRODUCTS = ROOT / "data" / "products"
DATA_STONES = ROOT / "data" / "stones.json"
DATA_SITE = ROOT / "data" / "site.json"
TEMPLATES = ROOT / "templates"
STYLES = ROOT / "styles"
ASSETS = ROOT / "assets"
PUBLIC = ROOT / "public"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def copy_static():
    """Copy styles/ and assets/ (logo, product photography once it
    exists) into public/ so the site actually has everything the
    templates reference. Without this step every page 404s on its
    stylesheet/images and silently falls back to unstyled defaults."""
    styles_dest = PUBLIC / "styles"
    if styles_dest.exists():
        shutil.rmtree(styles_dest)
    shutil.copytree(STYLES, styles_dest)
    print(f"Copied styles/ -> {styles_dest.relative_to(ROOT)}")

    if ASSETS.exists():
        assets_dest = PUBLIC / "assets"
        if assets_dest.exists():
            shutil.rmtree(assets_dest)
        shutil.copytree(ASSETS, assets_dest)
        print(f"Copied assets/ -> {assets_dest.relative_to(ROOT)}")


def build_homepage(env, all_products):
    site = load_json(DATA_SITE)
    template = env.get_template("homepage.html")

    featured = []
    for slug in site["featured_products"]:
        if slug in all_products:
            featured.append(all_products[slug])
        else:
            print(f"WARNING: featured product '{slug}' not found in data/products/")

    html = template.render(site=site, featured_products=featured)
    out_path = PUBLIC / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"Built homepage              -> {out_path.relative_to(ROOT)}")


def build_collection_overview(env):
    site = load_json(DATA_SITE)
    template = env.get_template("collection-overview.html")
    html = template.render(
        site=site,
        overview=site["collection_overview"],
        categories=site["categories"],
    )
    out_dir = PUBLIC / "collection"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"Built collection overview   -> {out_path.relative_to(ROOT)}")


def build_atelier(env):
    site = load_json(DATA_SITE)
    template = env.get_template("atelier.html")
    html = template.render(site=site, atelier=site["atelier"])
    out_dir = PUBLIC / "atelier"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"Built atelier                -> {out_path.relative_to(ROOT)}")


def build():
    copy_static()

    env = Environment(loader=FileSystemLoader(str(TEMPLATES)))
    template = env.get_template("product-page.html")
    stones = load_json(DATA_STONES)

    product_files = sorted(DATA_PRODUCTS.glob("*.json"))
    if not product_files:
        print("No product data files found in", DATA_PRODUCTS)
        return

    all_products = {}
    for product_file in product_files:
        product = load_json(product_file)
        all_products[product["slug"]] = product
        html = template.render(product=product, stones=stones)

        out_dir = PUBLIC / "products" / product["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "index.html"
        out_path.write_text(html, encoding="utf-8")

        print(f"Built {product['slug']:<25} -> {out_path.relative_to(ROOT)}")

    build_homepage(env, all_products)
    build_collection_overview(env)
    build_atelier(env)


if __name__ == "__main__":
    build()
