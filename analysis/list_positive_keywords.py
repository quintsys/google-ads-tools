#!/usr/bin/env python3
# Lists positive (non-negative) keywords in an ad group, with counts.
# Usage:
#   python list_positive_keywords.py --customer-id 6091332809 --ad-group-id 187136680689
#   python list_positive_keywords.py --customer-id 6091332809 --ad-group-id 187136680689 --to-csv positives.csv

import argparse, csv
from google.ads.googleads.client import GoogleAdsClient

def ga(client): return client.get_service("GoogleAdsService")

def qrows(client, cid, q): return list(ga(client).search(customer_id=cid, query=q))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--customer-id", required=True)
    ap.add_argument("--ad-group-id", required=True)
    ap.add_argument("--to-csv")
    args = ap.parse_args()

    client = GoogleAdsClient.load_from_storage()
    q = f"""
      SELECT
        ad_group_criterion.criterion_id,
        ad_group_criterion.status,
        ad_group_criterion.negative,
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        ad_group_criterion.cpc_bid_micros
      FROM ad_group_criterion
      WHERE ad_group_criterion.type = KEYWORD
        AND ad_group_criterion.negative = FALSE
        AND ad_group_criterion.ad_group = 'customers/{args.customer_id}/adGroups/{args.ad_group_id}'
    """
    rows = qrows(client, args.customer_id, q)

    by_match, by_status = {}, {}
    items = []
    for r in rows:
        kw = r.ad_group_criterion.keyword
        status = r.ad_group_criterion.status.name
        mt = kw.match_type.name
        bid = r.ad_group_criterion.cpc_bid_micros
        items.append({
            "id": r.ad_group_criterion.criterion_id,
            "text": kw.text,
            "match_type": mt,
            "status": status,
            "cpc_bid": (bid/1_000_000.0) if bid else None,
        })
        by_match[mt] = by_match.get(mt, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1

    print(f"Positive keywords in ad group {args.ad_group_id}: {len(items)}\n")
    if by_match:
        print("By match type:")
        for mt, n in sorted(by_match.items()):
            print(f"  {mt:<12} {n}")
        print()
    if by_status:
        print("By status:")
        for st, n in sorted(by_status.items()):
            print(f"  {st:<12} {n}")
        print()

    # print a few examples
    for it in items[:20]:
        bid_txt = f" | bid ${it['cpc_bid']:.2f}" if it["cpc_bid"] is not None else ""
        print(f"[{it['status']}] {it['match_type']}: {it['text']}{bid_txt}")
    if len(items) > 20:
        print(f"... (+{len(items)-20} more)")

    if args.to_csv:
        with open(args.to_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["id","text","match_type","status","cpc_bid"])
            w.writeheader()
            w.writerows(items)
        print(f"\nWrote CSV → {args.to_csv}")

if __name__ == "__main__":
    main()
