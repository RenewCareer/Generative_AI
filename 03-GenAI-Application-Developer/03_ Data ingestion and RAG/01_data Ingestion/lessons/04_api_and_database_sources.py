"""Lesson 4: ingest from an API and a database, not just files.

Starts a small local API, so no internet is needed.

Run: python lessons/04_api_and_database_sources.py
"""

import json
import sqlite3
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from project.ingest import load_api, load_sqlite, validate_records  # noqa: E402

TICKETS = [
    {"ticket_id": 501, "subject": "Speaker offline", "body": "Nimbus shows NB-17 after the router restart."},
    {"ticket_id": 502, "subject": "Late parcel", "body": "Tracking page shows SHP-404 for three days."},
]


class TicketAPI(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = json.dumps(TICKETS).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args) -> None:
        pass


def main() -> None:
    server = HTTPServer(("127.0.0.1", 0), TicketAPI)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        records = load_api(f"http://127.0.0.1:{server.server_port}/tickets", source="tickets")
    finally:
        server.shutdown()
    print("FROM A REST API")
    for document in validate_records(records).valid:
        print(f"  {document.doc_id}: {document.text.splitlines()[1]}")

    with tempfile.TemporaryDirectory() as temp:
        database = Path(temp, "crm.sqlite")
        connection = sqlite3.connect(database)
        connection.execute("CREATE TABLE articles (id INTEGER, title TEXT, body TEXT)")
        connection.execute(
            "INSERT INTO articles VALUES (1, 'Pairing', 'Hold the power button for 5 seconds until blue.')"
        )
        connection.commit()
        connection.close()
        records = load_sqlite(database, "SELECT id, title, body FROM articles", source="crm")

    print("\nFROM A DATABASE")
    for document in validate_records(records).valid:
        print(f"  {document.doc_id}: {document.text.splitlines()[2]}")

    print("\nDifferent systems, same SourceDocument contract. In production add authentication,")
    print("pagination, rate limits, and a 'last synced' cursor so that each run fetches only changes.")


if __name__ == "__main__":
    main()
