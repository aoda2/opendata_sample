"""CLI: import GTFS CSV files into SQLite.

Usage:
    python -m cmd.importer --data ./data/gtfs --db ./data/transit.db
"""
import sqlite3
import sys
from pathlib import Path

import click

# Allow running from backend/ directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from internal.gtfs.importer import import_gtfs


@click.command()
@click.option("--data", default="data/gtfs", show_default=True,
              help="Directory containing GTFS .txt files")
@click.option("--db", default="data/transit.db", show_default=True,
              help="SQLite database path (created if not exists)")
def main(data: str, db: str) -> None:
    data_dir = Path(data)
    db_path = Path(db)

    if not data_dir.exists():
        click.echo(f"Error: data directory '{data_dir}' does not exist.", err=True)
        raise SystemExit(1)

    db_path.parent.mkdir(parents=True, exist_ok=True)

    click.echo(f"Importing GTFS from {data_dir} → {db_path}")
    conn = sqlite3.connect(db_path)
    try:
        counts = import_gtfs(conn, data_dir)
    finally:
        conn.close()

    click.echo("Import complete:")
    for key, val in counts.items():
        click.echo(f"  {key}: {val:,}")


if __name__ == "__main__":
    main()
