"""Create the sample DOCX, HTML and XLSX files in data/raw, so each extractor has real input.

Run once: python make_samples.py
"""

from pathlib import Path

import pandas as pd
from docx import Document

RAW = Path(__file__).resolve().parent / "data" / "raw"

HTML = """<!doctype html>
<html><head><title>Shipping FAQ</title><style>body { color: red }</style>
<script>trackVisitor();</script></head>
<body>
<nav><a href="/">Home</a> <a href="/shop">Shop</a> <a href="/cart">Cart</a></nav>
<main>
  <h1>Shipping FAQ</h1>
  <h2>How long does delivery take?</h2>
  <p>Standard delivery takes 3 to 5 business days. Express takes 1 to 2 business days.</p>
  <h2>Delivery options</h2>
  <table>
    <tr><th>Option</th><th>Time</th><th>Cost</th></tr>
    <tr><td>Standard</td><td>3-5 days</td><td>Free above 75 dollars</td></tr>
    <tr><td>Express</td><td>1-2 days</td><td>12 dollars</td></tr>
  </table>
  <h2>What can I track?</h2>
  <ul><li>Dispatch date</li><li>Courier location</li><li>Expected delivery</li></ul>
</main>
<footer>Copyright Acme Retail. Subscribe to our newsletter.</footer>
</body></html>
"""


def make_docx(path):
    document = Document()
    document.add_heading("New Hire Onboarding Guide", level=1)
    document.add_heading("First week", level=2)
    document.add_paragraph("Collect your laptop from IT on day one. Complete the security training by Friday.")
    document.add_heading("Key contacts", level=2)
    table = document.add_table(rows=3, cols=2)
    for row, (team, email) in zip(
        table.rows,
        [("Team", "Email"), ("IT help desk", "it@acme.example"), ("People team", "people@acme.example")],
    ):
        row.cells[0].text, row.cells[1].text = team, email
    document.add_heading("Probation", level=2)
    document.add_paragraph("The probation period lasts 90 days, with a review meeting at day 45.")
    document.save(path)


def make_xlsx(path):
    products = pd.DataFrame(
        [
            {"sku": "AX2-BLK", "product": "Aurora X2", "price_usd": 149, "stock": 320},
            {"sku": "NB1-WHT", "product": "Nimbus speaker", "price_usd": 89, "stock": 145},
            {"sku": "TB3-GRN", "product": "Terra band", "price_usd": 59, "stock": 510},
        ]
    )
    stores = pd.DataFrame(
        [
            {"store": "Downtown", "city": "Lisbon", "manager": "R. Silva"},
            {"store": "Harbour", "city": "Porto", "manager": "M. Dias"},
        ]
    )
    with pd.ExcelWriter(path) as writer:
        products.to_excel(writer, sheet_name="Products", index=False)
        stores.to_excel(writer, sheet_name="Stores", index=False)


def main():
    for folder in ("docx", "html", "spreadsheets", "pdf"):
        (RAW / folder).mkdir(parents=True, exist_ok=True)
    make_docx(RAW / "docx" / "onboarding_guide.docx")
    (RAW / "html" / "shipping_faq.html").write_text(HTML, encoding="utf-8")
    make_xlsx(RAW / "spreadsheets" / "price_list.xlsx")
    print(f"Sample files written under {RAW}")


if __name__ == "__main__":
    main()
