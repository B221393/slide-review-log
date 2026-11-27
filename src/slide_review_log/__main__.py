"""Keep dated slide feedback and carry open items into the next revision."""

import argparse
from contextlib import closing
from datetime import date
import sqlite3
from pathlib import Path


def nonempty(value):
    value = value.strip()
    if not value:
        raise argparse.ArgumentTypeError("enter nonempty text")
    return value


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("enter a number greater than zero")
    return number


def iso_date(value):
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("enter a valid date in YYYY-MM-DD format") from exc


def build_parser():
    parser = argparse.ArgumentParser(prog="slide-review-log", description=__doc__)
    parser.add_argument("--db", type=Path, default=Path("slide-review.sqlite3"))
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="Record feedback against a specific deck version")
    add.add_argument("--deck", required=True, type=nonempty)
    add.add_argument("--version", required=True, type=nonempty)
    add.add_argument("--slide", required=True, type=positive_int)
    add.add_argument("--date", type=iso_date, default=date.today().isoformat())
    add.add_argument("comment", type=nonempty)

    show = commands.add_parser("list", help="List open feedback across previous versions")
    show.add_argument("--deck", required=True, type=nonempty)
    show.add_argument("--all", action="store_true", help="Include resolved feedback")

    resolve = commands.add_parser("resolve", help="Record the version that addressed an item")
    resolve.add_argument("id", type=positive_int)
    resolve.add_argument("--version", required=True, type=nonempty)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        with closing(sqlite3.connect(args.db)) as db, db:
            db.execute(
                """CREATE TABLE IF NOT EXISTS feedback (
                       id INTEGER PRIMARY KEY,
                       deck TEXT NOT NULL,
                       version TEXT NOT NULL,
                       slide INTEGER NOT NULL,
                       received_on TEXT NOT NULL,
                       comment TEXT NOT NULL,
                       resolved_in TEXT
                   )"""
            )
            if args.command == "add":
                row = db.execute(
                    """INSERT INTO feedback(deck, version, slide, received_on, comment)
                       VALUES (?, ?, ?, ?, ?)""",
                    (args.deck, args.version, args.slide, args.date, args.comment),
                )
                print(f"Added #{row.lastrowid}")
            elif args.command == "list":
                rows = db.execute(
                    """SELECT id, version, slide, received_on, comment, resolved_in
                       FROM feedback
                       WHERE deck = ? AND (? OR resolved_in IS NULL)
                       ORDER BY received_on, id""",
                    (args.deck, args.all),
                )
                for item_id, version, slide, received_on, comment, resolved_in in rows:
                    state = f"resolved in {resolved_in}" if resolved_in else "open"
                    print(f"#{item_id} {received_on} {version} p{slide} [{state}] {comment}")
            else:
                updated = db.execute(
                    "UPDATE feedback SET resolved_in = ? WHERE id = ? AND resolved_in IS NULL",
                    (args.version, args.id),
                )
                if updated.rowcount == 0:
                    parser.exit(1, f"Feedback #{args.id} was not found or is already resolved.\n")
                print(f"Resolved #{args.id} in {args.version}")
    except sqlite3.Error as exc:
        parser.exit(1, f"Database error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
