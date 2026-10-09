"""Generate the bundled mock shop (deterministic; run in the course venv).

Usage (from the repo root):
    python setup/mock_shop/build_shop.py

Builds a static e-commerce site that Sessions 17-19 crawl locally:

    setup/mock_shop/
    ├── index.html               # landing page, links to categories + page 1
    ├── robots.txt               # Session 17 politeness rules
    ├── sitemap.xml              # every URL, for the crawler frontier
    ├── category/<name>.html     # 4 category pages (30 products each)
    ├── products/page-1.html     # 4 listing pages x 30 products
    ├── products/page-2.html
    ├── products/page-3.html
    ├── products/page-4.html
    └── product/<id>.html        # 120 detail pages

Products come from ``datasets/fallback_products.json`` — the SAME 120 records
used as the offline fallback in Sessions 19-23 — so a live local crawl and the
fallback dataset stay identical in shape and values.

Serve it with (see setup/README.md):
    python -m http.server 8000
"""
from __future__ import annotations

import json
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRODUCTS_JSON = ROOT / "datasets" / "fallback_products.json"

PAGE_SIZE = 32  # 128 products / 32 = exactly 4 listing pages, as the syllabus asks
BASE = ""  # relative links keep the site portable (any host, any port)

STYLE = """    body { font-family: system-ui, sans-serif; margin: 0; color: #222; }
    header { background: #1f3b57; color: #fff; padding: 14px 24px; }
    header a { color: #cfe3ff; margin-right: 14px; text-decoration: none; }
    main { padding: 20px 24px; }
    .grid { display: flex; flex-wrap: wrap; gap: 16px; }
    .card { border: 1px solid #ddd; border-radius: 6px; padding: 12px;
            width: 300px; }
    .card h3 { margin: 0 0 6px; font-size: 15px; }
    .price { font-weight: bold; color: #1f3b57; }
    .cat { text-transform: uppercase; font-size: 11px; color: #888; }
    .pager { margin-top: 24px; }
    .pager a { margin-right: 10px; }
    table.meta td { padding-right: 18px; }"""


def load_products() -> list[dict]:
    """Read the shared 120-product dataset."""
    products = json.loads(PRODUCTS_JSON.read_text(encoding="utf-8"))
    if len(products) != 128:
        raise SystemExit(f"expected 128 products (120 + 8 near-dupes), got {len(products)}")
    return products


def page(title: str, body: str, nav: str) -> str:
    """Wrap body content in the shared site chrome."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{escape(title)} — Mock Shop</title>
  <style>
{STYLE}
  </style>
</head>
<body>
  <header>
    <strong>Mock Shop</strong>
    {nav}
  </header>
  <main>
{body}
  </main>
</body>
</html>
"""


def nav_html(extra: str = "") -> str:
    """Shared header navigation."""
    links = [
        f'<a href="{BASE}index.html">Home</a>',
        f'<a href="{BASE}products/page-1.html">All products</a>',
    ]
    for cat in ("electronics", "books", "kitchen", "sports"):
        links.append(f'<a href="{BASE}category/{cat}.html">{cat.title()}</a>')
    if extra:
        links.append(extra)
    return "\n    ".join(links)


def card_html(p: dict) -> str:
    """One product card, as used on index/category/listing pages."""
    return (
        f'    <div class="card" data-product-id="{p["id"]}">\n'
        f'      <span class="cat">{escape(p["category"])}</span>\n'
        f'      <h3><a href="{BASE}product/{p["id"]}.html">{escape(p["name"])}</a></h3>\n'
        f'      <p class="price">${p["price"]:.2f}</p>\n'
        f'      <p class="desc">{escape(p["description"])}</p>\n'
        f'    </div>'
    )


def pager_html(page_no: int, total_pages: int) -> str:
    """Previous/next pager, plus a numbered link list."""
    parts = []
    if page_no > 1:
        parts.append(f'<a href="{BASE}products/page-{page_no - 1}.html">&larr; Prev</a>')
    if page_no < total_pages:
        parts.append(f'<a href="{BASE}products/page-{page_no + 1}.html">Next &rarr;</a>')
    for n in range(1, total_pages + 1):
        if n == page_no:
            parts.append(f"<strong>{n}</strong>")
        else:
            parts.append(f'<a href="{BASE}products/page-{n}.html">{n}</a>')
    return '  <div class="pager">\n    ' + "\n    ".join(parts) + "\n  </div>"


def write(path: Path, text: str) -> None:
    """Create parent dirs and write UTF-8 text."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_index(products: list[dict]) -> None:
    """Landing page: first 12 products + links into the listing pages."""
    body = ["  <h1>Mock Shop</h1>",
            "  <p>A small static shop used for the IR course. 128 products, "
            "4 listing pages of 32, 4 categories.</p>",
            '  <div class="grid">']
    body += [card_html(p) for p in products[:12]]
    body.append("  </div>")
    body.append(pager_html(1, 4))
    write(HERE / "index.html", page("Home", "\n".join(body), nav_html()))


def build_listing(products: list[dict]) -> int:
    """Build products/page-N.html, PAGE_SIZE products per page."""
    total = len(products)
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    for page_no in range(1, total_pages + 1):
        lo = (page_no - 1) * PAGE_SIZE
        chunk = products[lo:lo + PAGE_SIZE]
        body = [f"  <h1>Products — page {page_no} of {total_pages}</h1>",
                f'  <p>Showing {lo + 1}–{lo + len(chunk)} of {total} products.</p>',
                '  <div class="grid">']
        body += [card_html(p) for p in chunk]
        body.append("  </div>")
        body.append(pager_html(page_no, total_pages))
        extra = nav_html()
        write(HERE / "products" / f"page-{page_no}.html",
              page(f"Products page {page_no}", "\n".join(body), extra))
    return total_pages


def build_categories(products: list[dict]) -> list[str]:
    """One page per category, listing that category's products."""
    cats: dict[str, list[dict]] = {}
    for p in products:
        cats.setdefault(p["category"], []).append(p)
    for cat, items in sorted(cats.items()):
        body = [f"  <h1>{escape(cat.title())}</h1>",
                f"  <p>{len(items)} products in this category.</p>",
                '  <div class="grid">']
        body += [card_html(p) for p in items]
        body.append("  </div>")
        write(HERE / "category" / f"{cat}.html",
              page(cat.title(), "\n".join(body), nav_html()))
    return sorted(cats)


def build_detail(products: list[dict]) -> None:
    """One detail page per product — the richest HTML for parser practice."""
    for p in products:
        body = [
            f'  <div class="product" data-product-id="{p["id"]}">',
            f'    <h1 class="name">{escape(p["name"])}</h1>',
            f'    <p class="price">${p["price"]:.2f}</p>',
            f'    <p class="cat">Category: {escape(p["category"])}</p>',
            f'    <p class="desc">{escape(p["description"])}</p>',
            "    <table class=\"meta\">",
            "      <tr><td>SKU</td><td>" + p["id"] + "</td></tr>",
            f'      <tr><td>Stock</td><td>{"In stock" if p["price"] < 400 else "Low stock"}</td></tr>',
            "    </table>",
            '    <p class="back"><a href="'
            f'{BASE}products/page-1.html">Back to products</a></p>',
            "  </div>",
        ]
        write(HERE / "product" / f'{p["id"]}.html',
              page(p["name"], "\n".join(body), nav_html()))


def build_robots() -> None:
    """robots.txt — the politeness contract Session 17's crawler obeys."""
    write(HERE / "robots.txt", """# Mock Shop — crawl policy for the IR course.
# Sessions 17-19 read this file and honour it exactly.
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /cart/

# Politeness: one request at a time, at most 1 per second.
Crawl-delay: 1
""")


def build_sitemap(total_pages: int, cats: list[str], products: list[dict]) -> None:
    """A sitemap of every URL — handy for testing the crawler's frontier."""
    urls = [f"{BASE}index.html"]
    urls += [f"{BASE}products/page-{n}.html" for n in range(1, total_pages + 1)]
    urls += [f"{BASE}category/{c}.html" for c in cats]
    urls += [f'{BASE}product/{p["id"]}.html' for p in products]
    body = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    body += [f"  <url><loc>{u}</loc></url>" for u in urls]
    body.append("</urlset>")
    write(HERE / "sitemap.xml", "\n".join(body) + "\n")


def main() -> None:
    """Regenerate the whole mock shop from the shared dataset."""
    products = load_products()
    cats = sorted({p["category"] for p in products})
    build_index(products)
    total_pages = build_listing(products)
    build_categories(products)
    build_detail(products)
    build_robots()
    build_sitemap(total_pages, cats, products)
    n_detail = len(list((HERE / "product").glob("*.html")))
    print(f"products: {len(products)}")
    print(f"categories: {len(cats)} -> {cats}")
    print(f"listing pages: {total_pages}")
    print(f"detail pages: {n_detail}")
    print(f"sitemap urls: {2 + total_pages + len(cats) + len(products)}")


if __name__ == "__main__":
    main()
