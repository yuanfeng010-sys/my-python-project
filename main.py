#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Node Report Analyzer
- Reads a CSV exported by your Clash node checker
- Ranks nodes by: risk_score (low better), error_count (low better), avg_latency_s (low better)
- Prints a clean table + optionally writes a ranked CSV
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import sys
from typing import Dict, List, Tuple, Any


def _to_float(x: Any) -> float:
    if x is None:
        return float("nan")
    s = str(x).strip()
    if s == "" or s.lower() in {"nan", "none", "null"}:
        return float("nan")
    try:
        return float(s)
    except ValueError:
        return float("nan")


def _to_int(x: Any) -> int:
    f = _to_float(x)
    if math.isnan(f):
        return 0
    return int(f)


def read_rows(csv_path: str) -> Tuple[List[str], List[Dict[str, str]]]:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    # Try utf-8-sig first (common for Excel-exported CSV), fallback to utf-8
    for enc in ("utf-8-sig", "utf-8"):
        try:
            with open(csv_path, "r", encoding=enc, newline="") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames or []
                rows = [r for r in reader]
                if not headers:
                    raise ValueError("CSV has no header row.")
                return headers, rows
        except UnicodeDecodeError:
            continue

    raise UnicodeDecodeError("utf-8", b"", 0, 1, "Failed to decode CSV with utf-8/utf-8-sig")


def analyze(headers: List[str], rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    err_cols = [h for h in headers if h.startswith("err_")]
    t_cols = [h for h in headers if h.startswith("t_") and h.endswith("_s")]

    out: List[Dict[str, Any]] = []
    for r in rows:
        node = (r.get("node") or "").strip() or "(unknown)"
        egress_ip = (r.get("egress_ip") or "").strip()
        country = (r.get("country") or "").strip()
        region = (r.get("region") or "").strip()
        org = (r.get("org") or r.get("domain") or "").strip()

        risk_score = _to_int(r.get("risk_score"))

        # error_count = how many err_* columns are non-empty
        error_count = 0
        error_keys: List[str] = []
        for c in err_cols:
            v = (r.get(c) or "").strip()
            if v != "":
                error_count += 1
                error_keys.append(c.replace("err_", ""))

        # avg latency across all t_*_s columns (ignore NaN)
        lat_values = [_to_float(r.get(c)) for c in t_cols]
        lat_values = [x for x in lat_values if not math.isnan(x)]
        avg_latency = sum(lat_values) / len(lat_values) if lat_values else float("inf")

        out.append(
            {
                "node": node,
                "egress_ip": egress_ip,
                "country": country,
                "region": region,
                "org": org,
                "risk_score": risk_score,
                "error_count": error_count,
                "errors": ",".join(error_keys) if error_keys else "",
                "avg_latency_s": avg_latency,
                "_raw": r,  # keep raw for optional CSV output
            }
        )

    # Sort: lowest risk_score, then lowest error_count, then lowest latency
    out.sort(key=lambda x: (x["risk_score"], x["error_count"], x["avg_latency_s"]))
    return out


def print_table(items: List[Dict[str, Any]], top: int) -> None:
    top_items = items[:top] if top > 0 else items

    # Simple console table
    headers = ["#", "risk", "err", "avg_s", "egress_ip", "country/region", "node"]
    print(" | ".join(headers))
    print("-" * 110)

    for i, it in enumerate(top_items, 1):
        avg_s = it["avg_latency_s"]
        avg_s_str = "inf" if avg_s == float("inf") else f"{avg_s:.3f}"
        loc = (it["country"] + "/" + it["region"]).strip("/")
        print(
            f"{i:>2} | "
            f"{it['risk_score']:<4} | "
            f"{it['error_count']:<3} | "
            f"{avg_s_str:<6} | "
            f"{it['egress_ip']:<15} | "
            f"{loc:<18} | "
            f"{it['node']}"
        )


def write_ranked_csv(original_headers: List[str], ranked: List[Dict[str, Any]], out_path: str) -> None:
    # Add a few computed columns to the front
    extra_cols = ["rank", "risk_score", "error_count", "avg_latency_s", "errors"]
    headers = extra_cols + [h for h in original_headers if h not in extra_cols]

    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for idx, it in enumerate(ranked, 1):
            row = dict(it["_raw"])
            row.update(
                {
                    "rank": idx,
                    "risk_score": it["risk_score"],
                    "error_count": it["error_count"],
                    "avg_latency_s": "inf" if it["avg_latency_s"] == float("inf") else f"{it['avg_latency_s']:.6f}",
                    "errors": it["errors"],
                }
            )
            writer.writerow(row)


def main() -> int:
    p = argparse.ArgumentParser(description="Analyze clash_node_report.csv and rank nodes.")
    p.add_argument("--csv", default="clash_node_report.csv", help="Path to report CSV (default: ./clash_node_report.csv)")
    p.add_argument("--top", type=int, default=10, help="Show top N nodes (default: 10)")
    p.add_argument("--out", default="", help="Write ranked CSV to this path (optional)")
    args = p.parse_args()

    headers, rows = read_rows(args.csv)
    ranked = analyze(headers, rows)

    print(f"Loaded {len(rows)} rows from: {args.csv}")
    print_table(ranked, args.top)

    if args.out:
        write_ranked_csv(headers, ranked, args.out)
        print(f"\nWrote ranked CSV to: {args.out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
