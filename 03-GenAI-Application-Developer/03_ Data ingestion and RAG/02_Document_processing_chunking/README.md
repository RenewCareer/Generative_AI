# Module 03.2: Document Processing and Chunking

**Slides:** [presentation.pptx](presentation.pptx) | **Time:** 3 hours | **Next:** [Module 03.3](../03_embedding_vector_search/README.md)

## Learning outcomes

By the end, students can:

- Extract PDF, Word, HTML and spreadsheet content, keeping its structure
- Clean text safely, removing noise without losing facts
- Compare fixed, sentence, recursive and heading-aware chunking
- Choose settings by measuring retrieval, not by following a tutorial

## Session plan

| Time | Activity | Material |
|---|---|---|
| 15 min | Slides: the four stages | `presentation.pptx` |
| 35 min | Extraction by format | `lessons/01_extract_every_format.py`, `src/extractors/` |
| 25 min | Cleaning | `lessons/02_cleaning_before_after.py`, `cleaners.py` |
| 35 min | Chunking, measured | `lessons/03_chunking_strategies.py`, `chunkers.py` |
| 20 min | The whole pipeline | `main.py`, `pipeline.py` |
| 40 min | Lab | Below |

## Concepts

**Extraction.** Every format fails differently:

| Format | Main problem | Approach |
|---|---|---|
| PDF | A layout format: broken lines, repeated headers | Extract by page, clean afterwards, and use OCR for scans |
| Word | Headings and tables get flattened | Keep reading order, and convert headings to Markdown |
| HTML | Menus and footers are noise | Prefer `<main>`, and remove scripts and navigation |
| Spreadsheets | Rows lose their column names | Write `column: value` on each row |

Spreadsheet aggregates such as "total sales" belong in SQL. Retrieval cannot sum a column.

**Cleaning.** Fix Unicode, rejoin hyphenated words, normalise whitespace, and remove lines that repeat
at the edges of most pages. The rule: if unsure, keep the text, because a lost fact cannot be retrieved.

**Chunking.** Retrieval needs pieces small enough to be precise, and large enough to make sense.

| Strategy | How it splits | Trade-off |
|---|---|---|
| Fixed size | Every N characters | Simple, but cuts words and sentences |
| Sentence | Whole sentences up to a limit | Reads well, but ignores sections |
| Recursive | Headings, then paragraphs, then sentences | A sensible default |
| Heading-aware | By section, with the heading path added | Keeps context with each chunk |

**Overlap** repeats a little text between neighbours, so a fact on a boundary survives in one chunk.

**Heading paths.** "Up to 60 dollars per day" means little alone. "Travel and Expense Policy > Meals"
makes the chunk retrievable, and understandable.

## Run it

```powershell
python make_samples.py
python lessons/01_extract_every_format.py
python lessons/02_cleaning_before_after.py
python lessons/03_chunking_strategies.py
python main.py
python main.py --strategy recursive --size 500 --overlap 50
python -m pytest tests
```

The sample files are already in `data/raw`, so `make_samples.py` is only needed to recreate them.
The NIST PDF is your own file, and `src/extractors/pdf_extractor.py` is your code, unchanged. If you
prefer your folder's existing `venv`, install `pytest` there and add `pip install -e ../..`.

### What to expect

`main.py` with the default settings:

```
Files processed : 4
Chunks written  : 206
Average size    : 588.1 characters
```

`lessons/03_chunking_strategies.py`, offline, on the 20 golden questions:

| Setting | Chunks | Answer in top 1 | In top 3 |
|---|---|---|---|
| Fixed, 150 | 36 | 85% | 95% |
| Recursive, 150 | 40 | 90% | 100% |
| Sentence, 150 | 40 | 100% | 100% |
| Heading, 300 | 29 | 100% | 100% |
| Fixed, 600 | 12 | 100% | 100% |

**Do not teach this as a universal ranking.** These are 8 short documents, searched with word-overlap
embeddings. What carries over is the method, and the idea that blind cuts can separate a fact from
the words that find it.

## Code walkthrough

| File | Teaching point |
|---|---|
| `pipeline.py` | Extract, clean, chunk, validate. A bad file is reported, and the rest continue |
| `schemas.py` | Each `ChunkRecord` has what it needs for citing and filtering |
| `cleaners.py` | `remove_repeated_lines` treats "Page 3" and "Page 4" as the same line |
| `chunkers.py` | One signature, so that strategies can be swapped and compared |
| `main.py` | Exit code 1 if any file failed, so that a scheduler can notice |

## A real bug to discuss

The first test for `remove_repeated_lines` used pages like "Body 1" and "Body 2". Because digits are
ignored when comparing lines, those bodies looked like repeated footers, and were deleted. The code
was doing what it was told, and the sample data was unrealistic. Good discussion: how could a real
document trigger this? Lines such as "Figure 1" and "Figure 2" at the page edge are a risk.

## Industry standards

- Keep structure, because headings and tables carry meaning
- Rich metadata on each chunk: source, page, index and strategy
- Layout-aware parsers for complex PDFs: try Docling, Unstructured, or `pymupdf4llm`
- OCR for pages with no text layer
- **Read your data:** look at samples of extracted chunks before indexing

## Lab

1. Run `main.py` with two strategies, and read five random chunks from each. Which would you trust?
2. Write three golden questions about the NIST PDF, and measure each strategy against them.
3. Try `pymupdf4llm`, and compare its output with the current PDF extractor.

**Marking notes.** Task 1 builds the habit of reading data. Task 2: a good question is "What are the four
functions of the AI RMF core?" (Govern, Map, Measure and Manage). Task 3: `pymupdf4llm` is in your folder's
`venv`, and in the course environment needs `pip install pymupdf4llm`. Look for preserved headings and tables.

## Check for understanding

1. Why is overlap useful? *A fact on a boundary still appears whole in at least one chunk.*
2. Why not make chunks as large as possible? *They cost more tokens, and dilute the search.*
3. A PDF page extracts as empty. What is likely? *It is a scanned image, and needs OCR.*
4. Why does changing the chunking strategy require re-indexing? *Existing vectors represent the old chunks.*
