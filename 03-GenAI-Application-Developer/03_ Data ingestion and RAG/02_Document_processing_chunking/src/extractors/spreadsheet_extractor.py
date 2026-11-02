import pandas as pd


def extract_spreadsheet(path, rows_per_page=25):
    """Turn rows into 'column: value' sentences, so each one makes sense on its own.

    A raw table loses its headers when split. Repeating them keeps every chunk meaningful.
    Each block of rows becomes one 'page', numbered across all sheets.
    """
    path = str(path)
    if path.lower().endswith(".csv"):
        sheets = {"csv": pd.read_csv(path)}
    else:
        sheets = pd.read_excel(path, sheet_name=None)

    extracted_pages = []

    for sheet_name, frame in sheets.items():
        frame = frame.dropna(how="all")
        lines = [
            "; ".join(f"{column}: {value}" for column, value in row.items() if pd.notna(value))
            for row in frame.to_dict(orient="records")
        ]
        for start in range(0, len(lines), rows_per_page):
            extracted_pages.append(
                {
                    "page_number": len(extracted_pages) + 1,
                    "content": f"# Sheet: {sheet_name}\n\n" + "\n".join(lines[start : start + rows_per_page]),
                }
            )

    return extracted_pages


if __name__ == "__main__":
    for page in extract_spreadsheet("data/raw/spreadsheets/price_list.xlsx"):
        print(page["content"][:500])
