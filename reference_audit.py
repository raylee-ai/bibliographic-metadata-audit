"""Compare two CSV snapshots of document-to-reference links."""

import argparse
import csv
import json
import re
import sys
from pathlib import Path


OPENALEX_URL = re.compile(r"https://openalex\.org/(W[0-9]+)/?")


def normalize_id(value):
    value = value.strip()
    match = OPENALEX_URL.fullmatch(value)
    return match.group(1) if match else value


def load_edges(path):
    edges = set()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = csv.reader(stream, strict=True)
        try:
            header = next(rows, [])
            required = ("document_id", "reference_id")
            if any(header.count(column) != 1 for column in required):
                raise ValueError(
                    f"{path}: header must contain document_id and reference_id once each"
                )
            document_index, reference_index = (header.index(column) for column in required)
            for row in rows:
                if not row:
                    continue
                location = f"{path}, line {rows.line_num}"
                if len(row) != len(header):
                    raise ValueError(f"{location}: expected {len(header)} columns, got {len(row)}")
                document = normalize_id(row[document_index])
                reference = normalize_id(row[reference_index])
                if not document or not reference:
                    raise ValueError(f"{location}: document_id and reference_id must be nonempty")
                edges.add((document, reference))
        except csv.Error as error:
            raise ValueError(f"{path}, line {rows.line_num}: {error}") from error
    return edges


def describe_edges(edges):
    return [
        {"document_id": document, "reference_id": reference}
        for document, reference in sorted(edges)
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path, help="source CSV snapshot")
    parser.add_argument("after", type=Path, help="imported CSV snapshot")
    args = parser.parse_args()
    try:
        before = load_edges(args.before)
        after = load_edges(args.after)
    except (OSError, ValueError) as error:
        parser.exit(2, f"error: {error}\n")

    lost = before - after
    added = after - before
    report = {
        "before_edges": len(before),
        "after_edges": len(after),
        "lost_edges": len(lost),
        "added_edges": len(added),
        "lost": describe_edges(lost),
        "added": describe_edges(added),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if lost or added else 0


if __name__ == "__main__":
    sys.exit(main())
