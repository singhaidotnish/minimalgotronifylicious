#!/usr/bin/env python3
import argparse, csv, json, os, sys

def row_value(row, *names):
    for n in names:
        v = row.get(n)
        if v:
            return v.strip()
    return ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=True, help="Path to NSE scrip-master CSV")
    ap.add_argument("-o", "--out", required=True, help="Output JSON path")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: Input CSV not found: {args.input}", file=sys.stderr)
        return 2
    if not os.path.isfile(args.input):
        print(f"ERROR: Input is not a file: {args.input}", file=sys.stderr)
        return 2

    out_items = []
    try:
        # newline='' recommended for csv; utf-8-sig tolerates BOM
        with open(args.input, "r", encoding="utf-8-sig", newline="") as fin:
            reader = csv.DictReader(fin)
            if not reader.fieldnames:
                print("ERROR: CSV has no header row — is this the right file?", file=sys.stderr)
                return 2
            for row in reader:
                ts = row_value(row, "TRADING_SYMBOL", "TRADINGSYMBOL", "TRADING SYMBOL", "SYMBOL")
                series = row_value(row, "SERIES")
                name = row_value(row, "NAME OF COMPANY", "NAME", "DESCRIPTION")

                label = ts or name or "?"
                symbol = None

                if ts:
                    symbol = ts if ":" in ts else f"NSE:{ts}"
                elif row.get("SYMBOL"):
                    token = f"{row['SYMBOL']}-{series}" if series else row["SYMBOL"]
                    symbol = f"NSE:{token}"

                if symbol:
                    out_items.append({"symbol": symbol, "label": label, "kind": "equity"})
    except Exception as e:
        print(f"ERROR: Failed to read CSV: {type(e).__name__}: {e}", file=sys.stderr)
        return 2

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fout:
        json.dump(out_items, fout, ensure_ascii=False, indent=2)

    print(f"Wrote {args.out} with {len(out_items)} entries")
    return 0

if __name__ == "__main__":
    sys.exit(main())
