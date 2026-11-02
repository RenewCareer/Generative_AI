from pathlib import Path

from bs4 import BeautifulSoup

NOISE_TAGS = ["script", "style", "nav", "footer", "aside", "form", "noscript"]
CONTENT_TAGS = ["h1", "h2", "h3", "h4", "p", "li", "tr", "pre"]


def extract_html(html_path):
    """Keep the article and drop the page furniture, which would pollute retrieval."""
    soup = BeautifulSoup(Path(html_path).read_text(encoding="utf-8"), "lxml")

    for tag in soup(NOISE_TAGS):
        tag.decompose()

    root = soup.find("main") or soup.find("article") or soup.body or soup
    parts = []

    for tag in root.find_all(CONTENT_TAGS):
        if tag.name == "tr":
            text = " | ".join(cell.get_text(" ", strip=True) for cell in tag.find_all(["th", "td"]))
        else:
            text = tag.get_text(" ", strip=True)
        if not text:
            continue
        if tag.name.startswith("h"):
            parts.append("#" * int(tag.name[1]) + " " + text)
        elif tag.name == "li":
            parts.append("- " + text)
        else:
            parts.append(text)

    return [{"page_number": 1, "content": "\n\n".join(parts)}]


if __name__ == "__main__":
    pages = extract_html("data/raw/html/shipping_faq.html")
    print(pages[0]["content"][:500])
