#!/usr/bin/env python3
import argparse, csv, json, os, sys

def row_value(row, *names):
    for n in names:
        if n in row and row[n]:
            return row[n].strip()
    return ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=True, help="NSE scrip-master CSV")
    ap.add_argument("-o", "--out", required=True, help="output JSON path")
    args = ap.parse_args()

    out = []
    with open(args.input, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            ts = row_value(row, "TRADING_SYMBOL", "TRADINGSYMBOL", "TOKEN", "SYMBOL")
            series = row_value(row, "SERIES")
            name = row_value(row, "NAME OF COMPANY", "NAME", "DESCRIPTION")

            label = ts or name or "?"
            symbol = None

            if ts:
                # assume already NSE/FO style token if it contains ':'; else treat as equity
                symbol = ts if ":" in ts else f"NSE:{ts}"
            elif row.get("SYMBOL"):
                token = f"{row['SYMBOL']}-{series}" if series else row['SYMBOL']
                symbol = f"NSE:{token}"

            if symbol:
                out.append({"symbol": symbol, "label": label, "kind": "equity"})

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"Wrote {args.out} with {len(out)} entries")

if __name__ == "__main__":
    sys.exit(main())
