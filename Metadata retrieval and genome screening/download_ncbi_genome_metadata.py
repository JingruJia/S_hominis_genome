#!/usr/bin/env python3
"""
Fetch NCBI genome metadata for assembly accessions listed in genome_info_list.txt.

Default output:
    genome_ncbi_info.csv

Example:
    python fetch_ncbi_genome_info.py
    python fetch_ncbi_genome_info.py -i genome_info_list.txt -o genome_ncbi_info.xlsx --xlsx

Optional:
    set NCBI_API_KEY=your_key
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


API_BASE = "https://api.ncbi.nlm.nih.gov/datasets/v2"
DATASETS_PAGE_BASE = "https://www.ncbi.nlm.nih.gov/datasets/genome"

FIELDNAMES = [
    "Genome_ID",
    "Accession",  # Assembly Name, e.g. ASM295410v1
    "Strain",
    "Taxon",
    "BioSample",
    "BioProject",
    "Isolation source",
    "Geographic location",
    "Host disease",
    "Level",
    "Size (Mb)",
    "GC%",
    "Scaffolds",
    "CDS",
    "Assembly accession",
    "Category",
    "Host",
    "URLs",
]

def read_accessions(path: Path) -> list[str]:
    accessions: list[str] = []
    seen: set[str] = set()
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            item = line.strip().split()[0] if line.strip() else ""
            if not item or item.startswith("#") or item in seen:
                continue
            seen.add(item)
            accessions.append(item)
    return accessions


def chunks(items: list[str], size: int) -> list[list[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def get_nested(obj: Any, path: list[str], default: Any = "") -> Any:
    cur = obj
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur if cur is not None else default



def get_any(obj: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in obj and obj[key] not in ("", None):
            return obj[key]
    return ""


def get_nested_any(obj: Any, *paths: list[str]) -> Any:
    for path in paths:
        value = get_nested(obj, path)
        if value not in ("", None):
            return value
    return ""
def first_nonempty(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            value = "; ".join(str(x) for x in value if x not in ("", None))
        text = str(value).strip()
        if text:
            return text
    return ""


def biosample_attribute(biosample: dict[str, Any], *names: str) -> str:
    wanted = {n.lower().replace("_", " ").replace("-", " ") for n in names}
    attrs = biosample.get("attributes") or []
    values: list[str] = []
    for attr in attrs:
        if not isinstance(attr, dict):
            continue
        name = first_nonempty(attr.get("name"), attr.get("attributeName"), attr.get("harmonizedName"))
        norm_name = name.lower().replace("_", " ").replace("-", " ")
        if norm_name in wanted:
            value = first_nonempty(attr.get("value"), attr.get("attributeValue"))
            if value and value not in values:
                values.append(value)
    return "; ".join(values)


def normalize_source_database(value: Any) -> str:
    text = first_nonempty(value)
    prefix = "SOURCE_DATABASE_"
    return text[len(prefix) :] if text.startswith(prefix) else text


def ncbi_get_json(url: str, api_key: str = "", timeout: int = 60, retries: int = 3) -> dict[str, Any]:
    headers = {
        "Accept": "application/json",
        "User-Agent": "python-fetch-ncbi-genome-info/1.0",
    }
    if api_key:
        headers["api-key"] = api_key

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=timeout) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                return json.loads(resp.read().decode(charset))
        except HTTPError as exc:
            last_error = exc
            if exc.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(2 * attempt)
                continue
            raise
        except (URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(2 * attempt)
                continue
            raise
    raise RuntimeError(f"NCBI request failed: {last_error}")


def fetch_dataset_reports(accessions: list[str], api_key: str, batch_size: int, sleep_sec: float) -> dict[str, dict[str, Any]]:
    reports_by_query: dict[str, dict[str, Any]] = {}
    total_batches = (len(accessions) + batch_size - 1) // batch_size

    for batch_no, batch in enumerate(chunks(accessions, batch_size), start=1):
        joined = ",".join(quote(acc, safe="") for acc in batch)
        params = urlencode({"page_size": max(batch_size, 100)})
        url = f"{API_BASE}/genome/accession/{joined}/dataset_report?{params}"
        print(f"[{batch_no}/{total_batches}] Fetching {len(batch)} accession(s) from NCBI...", file=sys.stderr)

        try:
            data = ncbi_get_json(url, api_key=api_key)
        except Exception as exc:
            print(f"WARNING: batch failed ({', '.join(batch)}): {exc}", file=sys.stderr)
            for acc in batch:
                reports_by_query.setdefault(acc, {})
            continue

        reports = data.get("reports") or []
        for report in reports:
            if not isinstance(report, dict):
                continue
            accession = first_nonempty(report.get("accession"), report.get("currentAccession"), report.get("current_accession"))
            current = first_nonempty(report.get("currentAccession"), report.get("current_accession"), accession)
            if accession:
                reports_by_query[accession] = report
            if current:
                reports_by_query[current] = report

        for acc in batch:
            reports_by_query.setdefault(acc, {})
        if sleep_sec > 0:
            time.sleep(sleep_sec)

    return reports_by_query


def row_from_report(query_accession: str, report: dict[str, Any]) -> dict[str, str]:
    assembly_info = get_any(report, "assembly_info", "assemblyInfo") or {}
    assembly_stats = get_any(report, "assembly_stats", "assemblyStats") or {}
    annotation_info = get_any(report, "annotation_info", "annotationInfo") or {}
    organism = report.get("organism") or {}
    biosample = get_any(assembly_info, "biosample") or {}
    biosample_desc = biosample.get("description") or {}
    biosample_org = biosample_desc.get("organism") or {}

    accession = first_nonempty(report.get("accession"), get_any(report, "current_accession", "currentAccession"), query_accession)
    # NCBI Assembly Name (assemblyInfo.assemblyName), not the GCF_/GCA_ accession.
    assembly_name = first_nonempty(
        get_any(assembly_info, "assembly_name", "assemblyName"),
        get_any(report, "assembly_name", "assemblyName"),
    )
    total_len = first_nonempty(get_any(assembly_stats, "total_sequence_length", "totalSequenceLength"))
    size_mb = ""
    if total_len:
        try:
            size_mb = f"{int(total_len) / 1_000_000:.3f}"
        except ValueError:
            size_mb = total_len

    strain = first_nonempty(
        get_nested_any(organism, ["infraspecific_names", "strain"], ["infraspecificNames", "strain"]),
        get_nested_any(biosample_org, ["infraspecific_names", "strain"], ["infraspecificNames", "strain"]),
        biosample.get("strain"),
        biosample_attribute(biosample, "strain"),
    )

    bioproject = first_nonempty(
        get_any(assembly_info, "bioproject_accession", "bioprojectAccession"),
        get_any(biosample, "bioproject_accession", "bioprojectAccession"),
        "; ".join(
            bp.get("accession", "")
            for lineage in get_any(assembly_info, "bioproject_lineage", "bioprojectLineage") or []
            for bp in lineage.get("bioprojects", []) or []
            if isinstance(bp, dict)
        ),
    )

    cds = first_nonempty(
        get_nested_any(
            annotation_info,
            ["stats", "gene_counts", "protein_coding"],
            ["stats", "geneCounts", "proteinCoding"],
        ),
    )

    source_db = normalize_source_database(get_any(report, "source_database", "sourceDatabase"))
    category = first_nonempty(get_any(assembly_info, "refseq_category", "refseqCategory"), source_db)

    return {
        "Genome_ID": query_accession,
        "Accession": assembly_name,
        "Strain": strain,
        "Taxon": first_nonempty(get_any(organism, "organism_name", "organismName"), get_any(biosample_org, "organism_name", "organismName")),
        "BioSample": first_nonempty(biosample.get("accession"), get_any(assembly_info, "biosample_accession", "biosampleAccession")),
        "BioProject": bioproject,
        "Isolation source": first_nonempty(
            get_any(biosample, "isolation_source", "isolationSource"),
            biosample_attribute(biosample, "isolation source", "isolation_source"),
        ),
        "Geographic location": first_nonempty(
            get_any(biosample, "geo_loc_name", "geoLocName"),
            biosample_attribute(biosample, "geographic location", "geo loc name", "geo_loc_name"),
        ),
        "Host disease": first_nonempty(
            get_any(biosample, "host_disease", "hostDisease"),
            biosample_attribute(biosample, "host disease", "host_disease"),
        ),
        "Level": first_nonempty(get_any(assembly_info, "assembly_level", "assemblyLevel")),
        "Size (Mb)": size_mb,
        "GC%": first_nonempty(get_any(assembly_stats, "gc_percent", "gcPercent")),
        "Scaffolds": first_nonempty(get_any(assembly_stats, "number_of_scaffolds", "numberOfScaffolds")),
        "CDS": cds,
        "Assembly accession": accession,
        "Category": category,
        "Host": first_nonempty(
            biosample.get("host"),
            biosample_attribute(biosample, "host"),
        ),
        "URLs": f"{DATASETS_PAGE_BASE}/{query_accession}/",
    }

def empty_row(accession: str) -> dict[str, str]:
    row = {name: "" for name in FIELDNAMES}
    row["Genome_ID"] = accession
    row["URLs"] = f"{DATASETS_PAGE_BASE}/{accession}/"
    return row


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_xlsx(rows: list[dict[str, str]], path: Path) -> None:
    try:
        from openpyxl import Workbook
        from openpyxl.utils import get_column_letter
    except ImportError as exc:
        raise SystemExit("openpyxl is not installed. Use CSV output or install openpyxl first.") from exc

    wb = Workbook()
    ws = wb.active
    ws.title = "NCBI_genome_info"
    ws.append(FIELDNAMES)
    for row in rows:
        ws.append([row.get(field, "") for field in FIELDNAMES])

    for idx, field in enumerate(FIELDNAMES, start=1):
        max_len = max([len(field)] + [len(str(row.get(field, ""))) for row in rows])
        ws.column_dimensions[get_column_letter(idx)].width = min(max_len + 2, 60)
    wb.save(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch NCBI genome metadata for assembly accessions and save a CSV/XLSX table."
    )
    parser.add_argument("-i", "--input", default="genome_info_list.txt", help="Input accession list, one accession per line.")
    parser.add_argument("-o", "--output", default="genome_ncbi_info.csv", help="Output file path.")
    parser.add_argument("--xlsx", action="store_true", help="Write XLSX instead of CSV. Requires openpyxl.")
    parser.add_argument("--api-key", default=os.environ.get("NCBI_API_KEY", ""), help="NCBI API key. Defaults to NCBI_API_KEY.")
    parser.add_argument("--batch-size", type=int, default=100, help="Number of accessions queried per request.")
    parser.add_argument("--sleep", type=float, default=0.34, help="Seconds to sleep between batches.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    # Fail early if Excel export is requested without the required dependency.
    # This prevents downloading all genome reports only to fail when saving.
    if args.xlsx or output_path.suffix.lower() == ".xlsx":
        try:
            import openpyxl  # noqa: F401
        except ImportError as exc:
            raise SystemExit(
                "openpyxl is not installed. Run: python -m pip install openpyxl"
            ) from exc

    accessions = read_accessions(input_path)
    if not accessions:
        raise SystemExit(f"No accessions found in {input_path}")

    reports = fetch_dataset_reports(
        accessions=accessions,
        api_key=args.api_key,
        batch_size=max(1, args.batch_size),
        sleep_sec=max(0.0, args.sleep),
    )

    rows = [
        row_from_report(acc, reports[acc]) if reports.get(acc) else empty_row(acc)
        for acc in accessions
    ]

    if args.xlsx or output_path.suffix.lower() == ".xlsx":
        write_xlsx(rows, output_path)
    else:
        write_csv(rows, output_path)

    print(f"Done. Wrote {len(rows)} row(s) to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
