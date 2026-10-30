"""``make build``: canonical tables from the pinned inputs.

- ``data/interim/aei_long.parquet``: every AEI release in canonical long form (PLAN 2.2);
- ``data/processed/regions.csv``: the Korean region table (PLAN 2.3);
- ``data/processed/denominators.csv``: the regional denominators of ADR 0005 (PLAN 4.1).
"""

import sys

from korea_ai_exposure import aei, paths, regional, regions


def main() -> int:
    frame = aei.build()
    print(f"wrote {aei.LONG_TABLE.relative_to(paths.ROOT).as_posix()}: {len(frame):,} rows")
    for release, count in frame.groupby("release").size().items():
        print(f"  {release}: {count:,} rows")
    regions.write_csv()
    csv_path = regions.CSV_PATH.relative_to(paths.ROOT).as_posix()
    print(f"wrote {csv_path}: {len(regions.REGIONS)} regions")
    regional.write_denominators()
    csv_path = regional.DENOMINATORS_CSV.relative_to(paths.ROOT).as_posix()
    print(f"wrote {csv_path}: {len(regional.SNAPSHOTS)} snapshots x 17 regions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
