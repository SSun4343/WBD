"""Preserve the last good world snapshot when CSV download or validation fails."""
import csv
import io
import json
import os
import re
from pathlib import Path


def parse_players(source):
    reader = csv.DictReader(io.StringIO(source.lstrip("\ufeff")))
    if not reader.fieldnames or not {"Name", "Index", "Team"}.issubset(reader.fieldnames):
        raise ValueError("Missing player headers")
    rows = []
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("Malformed player row")
        if not row["Name"].strip():
            if any(value.strip() for value in row.values()):
                raise ValueError("Player identity missing")
            continue
        for key in ("Index", "Team"):
            value = row[key].strip()
            if value and (not re.fullmatch(r"[0-9]+", value) or int(value) > 2147483647):
                raise ValueError("Invalid player number")
        rows.append(row)
    if not rows:
        raise ValueError("Empty player snapshot")
    return rows


def convert(source=Path("data.csv"), target=Path("data.json")):
    rows = parse_players(source.read_text(encoding="utf-8"))
    temporary = target.with_name(target.name + ".tmp")
    try:
        temporary.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    convert()

