# Module 03.1: Data Ingestion

**Slides:** [presentation.pptx](presentation.pptx) | **Time:** 2.5 hours | **Next:** [Module 03.2](../02_Document_processing_chunking/README.md)

## Learning outcomes

By the end, students can:

- Load files, APIs and databases into one document contract
- Validate at the door, and quarantine bad data instead of crashing
- Re-run a pipeline safely, using content hashes to find what changed
- Explain why missing deletes create "ghost" answers

## Session plan

| Time | Activity | Material |
|---|---|---|
| 15 min | Slides: where ingestion fits | `presentation.pptx` |
| 20 min | Review the exploration notebook | `Data_ingestion.ipynb` |
| 25 min | Loaders and one contract | `lessons/01_loaders_tour.py`, `lessons/04_api_and_database_sources.py` |
| 20 min | Validation and quarantine | `lessons/02_validation_quarantine.py` |
| 20 min | Incremental sync | `lessons/03_incremental_sync.py` |
| 15 min | Example app | `project/ingest.py` |
| 35 min | Lab | Below |

## Concepts

**One contract.** Whatever the source, every loader returns the same record: `doc_id`, `source`,
`source_type`, `title`, `text`, `metadata`. Later stages never need to know where data came from.

**Validate at the door.** A silent data bug becomes a confident wrong answer later. `SourceDocument`
enforces the contract with Pydantic, and adds checks such as a minimum amount of text.

**Quarantine, do not crash.** Bad records are set aside with a reason. One corrupt file should not
stop a nightly run, and a sudden jump in quarantine rate is an early warning that a source changed.

**Idempotent and incremental.** A SHA-256 hash of each document's text is compared to the manifest
from the last run:

| State | Meaning | Action |
|---|---|---|
| New | Not in the manifest | Process and add |
| Updated | Hash differs | Re-process, and replace old chunks |
| Unchanged | Same hash | Skip, and save time and money |
| Deleted | In the manifest only | Remove from the index too |

**From notebook to pipeline.** `Data_ingestion.ipynb` explores the problem, and its
`validate_documents` function is the same idea as `validate_records` here. A notebook explores, and a
pipeline operates: it logs, recovers, and can run again without duplicating work.

## Run it

```powershell
python lessons/01_loaders_tour.py
python lessons/02_validation_quarantine.py
python lessons/03_incremental_sync.py
python lessons/04_api_and_database_sources.py
python project/ingest.py
python project/ingest.py
python -m pytest tests
```

Run `project/ingest.py` twice on purpose. The first run adds 8 documents, and the second reports them
all unchanged. Results go to `output/kb/`.

### What to expect

```
1. First run               added=8 updated=0 unchanged=0 deleted=0
2. Run again, no changes   added=0 updated=0 unchanged=8 deleted=0
3. Edited one document     added=0 updated=1 unchanged=7 deleted=0
4. Deleted one document    added=0 updated=0 unchanged=7 deleted=1
```

## Code walkthrough: Knowledge Base Ingestor

| Part of `project/ingest.py` | Teaching point |
|---|---|
| `SourceDocument` | The contract, with its validator |
| `LOADERS` | Add a format by adding one function |
| `load_api` | Always set a timeout, and call `raise_for_status` |
| `load_sqlite` | `closing()` because sqlite3's context manager does not close the connection |
| `discover` | A bad file becomes a failure record, not a crash |
| `sync` | The hash comparison and the four states |

## Industry standards

- A schema contract at the entry point, for every source
- **Lineage:** each document records its source and ingestion time
- **Dead-letter handling:** bad data is kept and reported
- **Permissions captured at ingestion:** you cannot enforce at query time what you never recorded (Module 03.6)
- **Orchestrators** such as Airflow or Dagster schedule and retry these jobs in production
- **Know your data:** identify personal data, and follow your retention rules

## Lab

1. Add an Excel loader for `.xlsx` files that returns the standard record shape.
2. Quarantine documents with a `last_reviewed` date in their metadata older than one year.
3. Record the number of changed documents per run in a small run history file.

**Marking notes.** Task 1: register it in `LOADERS`, with one record per row, and use `pandas.read_excel`.
Task 2: raise `ValueError` inside validation so the existing quarantine path handles it. Test with one
fresh and one stale document. Task 3: append JSON lines rather than rewriting the file.

**Stretch:** add a real public API source with paging and a sync cursor.

## Check for understanding

1. Why use a hash rather than the file's modified date? *Dates change without content changing, and some sources have no reliable date.*
2. What goes wrong if deletes are ignored? *The assistant keeps quoting documents that no longer exist.*
3. Why is a rising quarantine rate useful? *It often signals that a source format has changed.*
