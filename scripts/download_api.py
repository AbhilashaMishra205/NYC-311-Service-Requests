import argparse
from urllib.parse import quote
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download NYC 311 data from Open Data API.")
    parser.add_argument(
        "--start-date",
        default="2019-12-31",
        help="Inclusive lower bound date used in created_date filter.",
    )
    parser.add_argument(
        "--end-date",
        default="2099-12-31",
        help="Inclusive upper bound date used in created_date filter.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)

    where_clause = (
        f"created_date>='{args.start_date}T00:00:00'"
        f" AND created_date<='{args.end_date}T23:59:59'"
    )
    encoded_where = quote(where_clause, safe="':><=")
    url = (
        "https://data.cityofnewyork.us/resource/erm2-nwe9.csv"
        f"?$where={encoded_where}"
        "&$order=created_date%20ASC"
        "&$limit=1000"
    )

    print(
        "Downloading data from NYC Open Data API "
        f"(start date: {args.start_date}, end date: {args.end_date})..."
    )
    df = pd.read_csv(url)

    output_path = raw_dir / "present.csv"
    df.to_csv(output_path, index=False)

    print(f"Download complete! File saved to {output_path}")


if __name__ == "__main__":
    main()
