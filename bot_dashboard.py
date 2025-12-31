#!/usr/bin/env python3
"""
Bot Dashboard (simple, offline)
- Logs snapshots for multiple bots (pair, price, profit, note)
- Shows current status (last snapshot per bot)
- Plots per-bot history (profit_usdt or price)
Designed to run on PyDroid (Android) or desktop Python 3.
No exchange API needed.
"""

import argparse
import csv
import os
import sys
import datetime as dt

DATA_DIR = os.path.join(os.path.dirname(__file__), "bot_logs")
os.makedirs(DATA_DIR, exist_ok=True)

FIELDS = ["timestamp", "bot", "pair", "price", "profit_usdt", "note"]

def csv_path(bot):
    safe = "".join(c for c in bot if c.isalnum() or c in ("_", "-"))
    return os.path.join(DATA_DIR, f"{safe}.csv")

def now_iso():
    return dt.datetime.now().isoformat(timespec="seconds")

def ensure_file(path):
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()

def log_snapshot(args):
    path = csv_path(args.bot)
    ensure_file(path)
    row = {
        "timestamp": args.timestamp or now_iso(),
        "bot": args.bot,
        "pair": args.pair or "",
        "price": f"{args.price:.10f}" if args.price is not None else "",
        "profit_usdt": f"{args.profit_usdt:.6f}" if args.profit_usdt is not None else "",
        "note": args.note or "",
    }
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writerow(row)
    print(f"Logged snapshot for {args.bot} -> {path}")
    print(row)

def status(args):
    import glob
    files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    if not files:
        print("No logs yet. Use the 'log' command first.")
        return
    print("Last snapshot per bot:\n")
    for path in sorted(files):
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            if len(rows) == 0:
                continue
            last = rows[-1]
            print(f"- {last['bot']}: {last['pair']} @ {last.get('price','')} | PnL {last.get('profit_usdt','')} | {last['timestamp']} | {last.get('note','')}")
    print("\nTip: 'python bot_dashboard.py plot --bot ZBCN --metric profit'")

def plot(args):
    import matplotlib.pyplot as plt
    path = csv_path(args.bot)
    if not os.path.exists(path):
        print(f"No log for bot '{args.bot}'. Log first with: python bot_dashboard.py log --bot {args.bot} --price 1.23 --profit_usdt 0.45")
        return
    ts = []
    y = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                ts.append(dt.datetime.fromisoformat(row["timestamp"]))
                val = float(row["profit_usdt"] if args.metric == "profit" else row["price"])
                y.append(val)
            except Exception:
                continue
    if not ts:
        print("Nothing to plot yet.")
        return
    plt.figure()
    plt.plot(ts, y)
    plt.title(f"{args.bot} ({args.metric})")
    plt.xlabel("Time")
    plt.ylabel("USDT" if args.metric=="profit" else "Price")
    plt.tight_layout()
    plt.show()

def export_all(args):
    # Merge all bot logs into a single CSV (wide format)
    import glob
    import collections
    files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    if not files:
        print("No logs to export.")
        return
    # Gather rows keyed by timestamp
    by_ts = collections.defaultdict(dict)
    bots = []
    for path in files:
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            if not rows: 
                continue
            bot_name = rows[-1]["bot"] if rows else os.path.splitext(os.path.basename(path))[0]
            bots.append(bot_name)
            for row in rows:
                ts = row["timestamp"]
                by_ts[ts][f"{bot_name}_price"] = row.get("price","")
                by_ts[ts][f"{bot_name}_profit"] = row.get("profit_usdt","")
    out_path = os.path.join(DATA_DIR, "dashboard_export.csv")
    all_fields = ["timestamp"] + [f"{b}_price" for b in bots] + [f"{b}_profit" for b in bots]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=all_fields)
        w.writeheader()
        for ts in sorted(by_ts.keys()):
            row = {"timestamp": ts}
            row.update(by_ts[ts])
            w.writerow(row)
    print(f"Exported wide CSV to {out_path}")

def main():
    p = argparse.ArgumentParser(description="Simple multi-bot dashboard (offline)")
    sub = p.add_subparsers()

    p_log = sub.add_parser("log", help="Log a snapshot for a bot")
    p_log.add_argument("--bot", required=True, help="Bot name e.g., ZBCN_grid or AVNT_manual")
    p_log.add_argument("--pair", default="", help="Trading pair e.g., ZBCN/USDT")
    p_log.add_argument("--price", type=float, help="Current price")
    p_log.add_argument("--profit_usdt", type=float, help="Realized/Current profit in USDT (your choice)")
    p_log.add_argument("--note", default="", help="Freeform note")
    p_log.add_argument("--timestamp", default=None, help="Override timestamp ISO (optional)")
    p_log.set_defaults(func=log_snapshot)

    p_status = sub.add_parser("status", help="Show last snapshot per bot")
    p_status.set_defaults(func=status)

    p_plot = sub.add_parser("plot", help="Plot history for one bot")
    p_plot.add_argument("--bot", required=True)
    p_plot.add_argument("--metric", choices=["profit","price"], default="profit")
    p_plot.set_defaults(func=plot)

    p_export = sub.add_parser("export", help="Export a wide CSV of all bots")
    p_export.set_defaults(func=export_all)

    if len(sys.argv) == 1:
        p.print_help()
        print("\nExamples:")
        print("  python bot_dashboard.py log --bot ZBCN_grid --pair ZBCN/USDT --price 0.0042376 --profit_usdt 0.35 --note '30 grids'")
        print("  python bot_dashboard.py log --bot ASTER_smart --pair ASTER/USDT --price 1.4703 --profit_usdt 0.07")
        print("  python bot_dashboard.py status")
        print("  python bot_dashboard.py plot --bot ZBCN_grid --metric profit")
        print("  python bot_dashboard.py export")
        sys.exit(0)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
