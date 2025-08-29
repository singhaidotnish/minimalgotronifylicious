#!/usr/bin/env python3
import argparse, json, requests, os, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", required=True, help="output JSON path")
    ap.add_argument("--futures", action="store_true", help="use futures API")
    ap.add_argument("--testnet", action="store_true", help="use testnet endpoints")
    args = ap.parse_args()

    if args.futures:
        base = "https://fapi.binance.com" if not args.testnet else "https://testnet.binancefuture.com"
        path = "/fapi/v1/exchangeInfo"
    else:
        base = "https://api.binance.com" if not args.testnet else "https://testnet.binance.vision"
        path = "/api/v3/exchangeInfo"

    r = requests.get(base + path, timeout=20)
    r.raise_for_status()
    data = r.json()

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Wrote {args.out} with {len(data.get('symbols', []))} symbols")

if __name__ == "__main__":
    sys.exit(main())
