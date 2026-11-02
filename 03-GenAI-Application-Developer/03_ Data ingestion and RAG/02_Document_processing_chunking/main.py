"""Example application: Document Processor, turning a folder of mixed files into chunks.

Run: python main.py
     python main.py --strategy recursive --size 500 --overlap 50
"""

import argparse
import sys
from pathlib import Path

from chunkers import STRATEGIES
from pipeline import run_pipeline

BASE_DIR = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=BASE_DIR / "data" / "raw")
    parser.add_argument("--output", type=Path, default=BASE_DIR / "data" / "processed" / "chunks.jsonl")
    parser.add_argument("--strategy", choices=sorted(STRATEGIES), default="heading")
    parser.add_argument("--size", type=int, default=800)
    parser.add_argument("--overlap", type=int, default=100)
    args = parser.parse_args()

    report = run_pipeline(args.input, args.output, args.strategy, args.size, args.overlap)

    print(f"Files processed : {report.files_processed}")
    print(f"Chunks written  : {report.chunks}")
    print(f"Average size    : {report.average_chunk_chars} characters")
    print(f"Output          : {args.output}")
    for failure in report.files_failed:
        print(f"FAILED          : {failure}")
    return 1 if report.files_failed else 0


if __name__ == "__main__":
    sys.exit(main())
