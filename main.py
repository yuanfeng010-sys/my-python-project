import argparse
import csv
import os
import random
from typing import List, Dict, Any


DEFAULT_CSV = "./clash_node_report.csv"


def write_demo_csv(path: str, n: int = 30) -> None:
    random.seed(42)
    rows = []
    for i in range(n):
        rows.append({
            "node": f"node_{i+1:02d}",
            "risk_score": round(random.uniform(0, 1), 4),
            "error_count": random.randint(0, 30),
            "avg_latency_s": round(random.uniform(0.1, 3.0), 4),
        })

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["node", "risk_score", "error_count", "avg_latency_s"])
        w.writeheader()
        w.writerows(rows)


def read_csv(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = []
        for row in r:
            # 允许列名略有变化时更鲁棒一点
            rows.append(row)
        return rows


def to_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def to_int(x: Any, default: int = 0) -> int:
    try:
        return int(float(x))
    except Exception:
        return default


def rank_nodes(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # 期望列名：node, risk_score, error_count, avg_latency_s
    ranked = []
    for row in rows:
        node = row.get("node") or row.get("name") or row.get("server") or "unknown"
        risk = to_float(row.get("risk_score"))
        err = to_int(row.get("error_count"))
        lat = to_float(row.get("avg_latency_s") or row.get("avg_latency") or row.get("latency"))

        # 简单综合评分：越低越好
        score = risk * 100 + err * 2 + lat * 10

        ranked.append({
            "node": node,
            "risk_score": risk,
            "error_count": err,
            "avg_latency_s": lat,
            "final_score": round(score, 4),
        })

    ranked.sort(key=lambda x: x["final_score"])
    return ranked


def write_ranked_csv(path: str, ranked: List[Dict[str, Any]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["rank", "node", "final_score", "risk_score", "error_count", "avg_latency_s"])
        w.writeheader()
        for i, row in enumerate(ranked, start=1):
            w.writerow({
                "rank": i,
                **row
            })


def main():
    parser = argparse.ArgumentParser(description="Analyze clash_node_report.csv and rank nodes.")
    parser.add_argument("--csv", dest="csv_path", default=DEFAULT_CSV,
                        help=f"Path to report CSV (default: {DEFAULT_CSV})")
    parser.add_argument("--top", dest="top_n", type=int, default=10,
                        help="Show top N nodes (default: 10)")
    parser.add_argument("--out", dest="out_path", default="",
                        help="Write ranked CSV to this path (optional)")
    parser.add_argument("--demo", action="store_true",
                        help="Generate a demo clash_node_report.csv in repo root, then rank it")

    args = parser.parse_args()

    if args.demo:
        demo_path = args.csv_path
        write_demo_csv(demo_path, n=30)
        print(f"[demo] wrote: {demo_path}")

    if not os.path.exists(args.csv_path):
        raise SystemExit(f"CSV not found: {args.csv_path}\nTip: run with --demo or provide --csv <path>")

    rows = read_csv(args.csv_path)
    ranked = rank_nodes(rows)
    top = ranked[: max(0, args.top_n)]

    print(f"Top {len(top)} nodes (lower score is better):")
    for r in top:
        print(f"- {r['node']}: score={r['final_score']} risk={r['risk_score']} err={r['error_count']} lat={r['avg_latency_s']}s")

    if args.out_path:
        write_ranked_csv(args.out_path, ranked)
        print(f"[out] wrote ranked csv: {args.out_path}")


if __name__ == "__main__":
    main()
