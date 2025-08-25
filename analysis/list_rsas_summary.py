#!/usr/bin/env python3
"""
List summary of Responsive Search Ads in an ad group:
- final URLs
- up to 3 headlines
- up to 2 descriptions

Usage:
  python list_rsas_summary.py \
    --customer-id 6091332809 \
    --ad-group-id 187136680689
"""

import argparse
from google.ads.googleads.client import GoogleAdsClient


def ga(client):
    return client.get_service("GoogleAdsService")


def qrows(client, customer_id, query: str):
    return list(ga(client).search(customer_id=customer_id, query=query))


def list_rsas(client, customer_id, ad_group_id):
    query = f"""
      SELECT
        ad_group_ad.ad.responsive_search_ad.headlines,
        ad_group_ad.ad.responsive_search_ad.descriptions,
        ad_group_ad.ad.final_urls,
        ad_group_ad.status
      FROM ad_group_ad
      WHERE ad_group_ad.ad_group = 'customers/{customer_id}/adGroups/{ad_group_id}'
        AND ad_group_ad.ad.type = RESPONSIVE_SEARCH_AD
    """

    rows = qrows(client, customer_id, query)

    print(f"Found {len(rows)} RSAs in ad group {ad_group_id}\n")
    for i, r in enumerate(rows, 1):
        ad = r.ad_group_ad.ad
        rsa = ad.responsive_search_ad
        print(f"RSA {i} (status={r.ad_group_ad.status.name}):")
        if ad.final_urls:
            print(f"  Final URL: {ad.final_urls[0]}")
        # first 3 headlines
        heads = [h.text for h in rsa.headlines[:3] if h.text]
        print("  Headlines: " + " | ".join(heads))
        # first 2 descriptions
        descs = [d.text for d in rsa.descriptions[:2] if d.text]
        print("  Descriptions: " + " | ".join(descs))
        print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--customer-id", required=True)
    ap.add_argument("--ad-group-id", required=True)
    args = ap.parse_args()

    client = GoogleAdsClient.load_from_storage()
    list_rsas(client, args.customer_id, args.ad_group_id)


if __name__ == "__main__":
    main()
