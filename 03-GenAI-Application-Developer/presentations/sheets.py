"""Combine rendered slides into contact sheets for review. Run after render.ps1."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

out = Path(__file__).parent / "_render"
for folder in sorted(p for p in out.iterdir() if p.is_dir() and p.name != "ui"):
    slides = sorted(folder.glob("s*.png"))
    if not slides:
        continue
    cols, tw, th = 2, 900, 506
    for page in range(0, len(slides), 6):
        chunk = slides[page:page + 6]
        rows = (len(chunk) + 1) // 2
        sheet = Image.new("RGB", (cols * tw + (cols + 1) * 10, rows * th + (rows + 1) * 10), "#888888")
        for i, path in enumerate(chunk):
            image = Image.open(path).convert("RGB").resize((tw, th))
            sheet.paste(image, (10 + (i % cols) * (tw + 10), 10 + (i // cols) * (th + 10)))
        sheet.save(out / f"sheet_{folder.name}_{page // 6}.jpg", quality=82)
print(sorted(p.name for p in out.glob("sheet_*.jpg")))
