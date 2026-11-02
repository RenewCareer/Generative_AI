import pymupdf

def extract_pdf(pdf_path): 

    document = pymupdf.open(pdf_path)

    extracted_pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text("text", sort=True)
        extracted_pages.append({
            "page_number": page_number, 
            "content": text
        })

    document.close()
    return extracted_pages

if __name__ == "__main__":

    pages = extract_pdf("data/raw/pdf/NIST.AI.100-1.pdf")

    for page in pages[:3]:

        print(f"\nPAGE {page['page_number']}")
        print(page["content"][:500])  # Print the first 500 characters of each page's content
        