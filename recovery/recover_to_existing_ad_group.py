#!/usr/bin/env python3
"""
Copy keywords (positives + optional negatives) and RSAs from a REMOVED ad group
into an EXISTING ad group. Idempotent (safe to re-run): dedupes keywords by
(text, match_type, negative_flag) and RSAs by (headlines, descriptions, urls, path1, path2).

Examples:

# Dry-run with negatives:
python recover_to_existing_ad_group.py \
  --customer-id 6091332809 \
  --source-ad-group-id 65028146118 \
  --dest-ad-group-id 187136680689 \
  --dry-run \
  --copy-negatives

# Execute (force Exact for positives, create paused, and copy negatives):
python recover_to_existing_ad_group.py \
  --customer-id 6091332809 \
  --source-ad-group-id 65028146118 \
  --dest-ad-group-id 187136680689 \
  --only-exact \
  --pause-on-create \
  --copy-negatives
"""

import argparse
from google.ads.googleads.client import GoogleAdsClient


def ga(client):
    return client.get_service("GoogleAdsService")


def qrows(client, customer_id: str, query: str):
    return list(ga(client).search(customer_id=customer_id, query=query))


def get_removed_ad_group(client, customer_id, ad_group_id):
    query = f"""
      SELECT
        ad_group.id, ad_group.name, ad_group.status, ad_group.campaign
      FROM ad_group
      WHERE ad_group.id = {ad_group_id}
      LIMIT 1
    """
    rows = qrows(client, customer_id, query)
    return rows[0] if rows else None


def get_keywords_for_ad_group(client, customer_id, ad_group_id):
    query = f"""
      SELECT
        ad_group_criterion.criterion_id,
        ad_group_criterion.status,
        ad_group_criterion.negative,
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type
      FROM ad_group_criterion
      WHERE ad_group_criterion.ad_group = 'customers/{customer_id}/adGroups/{ad_group_id}'
        AND ad_group_criterion.type = KEYWORD
    """
    return qrows(client, customer_id, query)


def get_rsas_for_ad_group(client, customer_id, ad_group_id):
    query = f"""
      SELECT
        ad_group_ad.ad.id,
        ad_group_ad.status,
        ad_group_ad.ad.final_urls,
        ad_group_ad.ad.responsive_search_ad.headlines,
        ad_group_ad.ad.responsive_search_ad.descriptions,
        ad_group_ad.ad.responsive_search_ad.path1,
        ad_group_ad.ad.responsive_search_ad.path2
      FROM ad_group_ad
      WHERE ad_group_ad.ad_group = 'customers/{customer_id}/adGroups/{ad_group_id}'
        AND ad_group_ad.ad.type = RESPONSIVE_SEARCH_AD
    """
    return qrows(client, customer_id, query)


def get_existing_keyword_set(client, customer_id, dest_ad_group_id):
    rows = get_keywords_for_ad_group(client, customer_id, dest_ad_group_id)
    exists = set()
    for r in rows:
        c = r.ad_group_criterion
        text = c.keyword.text.strip().lower()
        mt = c.keyword.match_type.name
        neg = bool(c.negative)
        exists.add((text, mt, neg))
    return exists


def get_existing_rsa_fingerprints(client, customer_id, dest_ad_group_id):
    rows = get_rsas_for_ad_group(client, customer_id, dest_ad_group_id)
    fps = set()
    for r in rows:
        ad = r.ad_group_ad.ad
        rsa = ad.responsive_search_ad
        if not rsa:
            continue
        h = tuple(sorted([a.text.strip() for a in rsa.headlines]))
        d = tuple(sorted([a.text.strip() for a in rsa.descriptions]))
        urls = tuple(sorted(ad.final_urls))
        path1 = rsa.path1
        path2 = rsa.path2
        fps.add((h, d, urls, path1, path2))
    return fps


def create_keywords(client, customer_id, dest_ag_res, source_kw_rows,
                    existing_set, only_exact=False, pause_on_create=False,
                    dedupe=True, copy_negatives=False):
    svc = client.get_service("AdGroupCriterionService")
    ops = []

    for r in source_kw_rows:
        c = r.ad_group_criterion
        text = c.keyword.text.strip()
        mt_enum = c.keyword.match_type if not only_exact else client.enums.KeywordMatchTypeEnum.EXACT
        mt_name = mt_enum.name
        is_negative = bool(c.negative)

        # Skip negatives unless the flag is set
        if is_negative and not copy_negatives:
            continue

        key = (text.lower(), mt_name, is_negative)
        if dedupe and key in existing_set:
            continue

        op = client.get_type("AdGroupCriterionOperation")
        kw = op.create
        kw.ad_group = dest_ag_res
        kw.keyword.text = text
        kw.keyword.match_type = mt_enum
        kw.negative = is_negative

        if not is_negative:
            # Positives can be enabled/paused
            kw.status = (client.enums.AdGroupCriterionStatusEnum.PAUSED
                         if pause_on_create else client.enums.AdGroupCriterionStatusEnum.ENABLED)
        # Negatives have no enabled/paused state; just create them.

        ops.append(op)

    if ops:
        svc.mutate_ad_group_criteria(customer_id=customer_id, operations=ops)
    return len(ops)


def create_rsas(client, customer_id, dest_ag_res, source_ad_rows,
                existing_fps, pause_on_create=False, dedupe=True):
    svc = client.get_service("AdGroupAdService")
    AdGroupAdStatusEnum = client.enums.AdGroupAdStatusEnum
    ops = []
    for r in source_ad_rows:
        ad = r.ad_group_ad.ad
        rsa = ad.responsive_search_ad
        if not rsa:
            continue
        h = tuple(sorted([a.text.strip() for a in rsa.headlines]))
        d = tuple(sorted([a.text.strip() for a in rsa.descriptions]))
        urls = tuple(sorted(ad.final_urls))
        path1 = rsa.path1
        path2 = rsa.path2
        fp = (h, d, urls, path1, path2)
        if dedupe and fp in existing_fps:
            continue

        op = client.get_type("AdGroupAdOperation")
        aga = op.create
        aga.ad_group = dest_ag_res
        aga.status = (AdGroupAdStatusEnum.PAUSED
                      if pause_on_create else AdGroupAdStatusEnum.ENABLED)
        new_ad = aga.ad
        new_ad.final_urls.extend(ad.final_urls)
        new_rsa = new_ad.responsive_search_ad
        for hh in rsa.headlines:
            asset = client.get_type("AdTextAsset"); asset.text = hh.text
            new_rsa.headlines.append(asset)
        for dd in rsa.descriptions:
            asset = client.get_type("AdTextAsset"); asset.text = dd.text
            new_rsa.descriptions.append(asset)
        if path1: new_rsa.path1 = path1
        if path2: new_rsa.path2 = path2
        ops.append(op)

    if ops:
        svc.mutate_ad_group_ads(customer_id=customer_id, operations=ops)
    return len(ops)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--customer-id", required=True)
    ap.add_argument("--source-ad-group-id", required=True, help="REMOVED ad group ID (numeric)")
    ap.add_argument("--dest-ad-group-id", required=True, help="EXISTING ad group ID (numeric)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pause-on-create", action="store_true")
    ap.add_argument("--no-dedupe", action="store_true")
    ap.add_argument("--only-exact", action="store_true")
    ap.add_argument("--copy-negatives", action="store_true",
                    help="Also copy negative keywords from source to destination")
    args = ap.parse_args()

    client = GoogleAdsClient.load_from_storage()

    # --- Source (removed) ad group summary
    src = get_removed_ad_group(client, args.customer_id, args.source_ad_group_id)
    if not src:
        raise SystemExit("Source ad group not found. Tip: ID must be correct; status may be REMOVED.")
    print(f"Source ad group: {src.ad_group.name} (status={src.ad_group.status.name})")

    dest_ag_res = f"customers/{args.customer_id}/adGroups/{args.dest_ad_group_id}"

    # --- Destination ad group name & campaign for human-friendly confirmation
    q = f"""
      SELECT
        ad_group.id,
        ad_group.name,
        ad_group.status,
        campaign.id,
        campaign.name
      FROM ad_group
      WHERE ad_group.id = {args.dest_ad_group_id}
      LIMIT 1
    """
    rows = qrows(client, args.customer_id, q)
    if rows:
        r = rows[0]
        dest_name = r.ad_group.name
        dest_status = r.ad_group.status.name
        campaign_name = r.campaign.name
        print(f"Destination ad group: {dest_name} (status={dest_status}) in campaign '{campaign_name}'")
    else:
        print(f"Destination ad group: {dest_ag_res}")

    # --- Load assets
    src_keywords = get_keywords_for_ad_group(client, args.customer_id, args.source_ad_group_id)
    src_ads = get_rsas_for_ad_group(client, args.customer_id, args.source_ad_group_id)
    print(f"Found {len(src_keywords)} keywords and {len(src_ads)} RSAs in source.")

    existing_kw = get_existing_keyword_set(client, args.customer_id, args.dest_ad_group_id)
    existing_ads = get_existing_rsa_fingerprints(client, args.customer_id, args.dest_ad_group_id)
    print(f"Destination currently has {len(existing_kw)} keywords and {len(existing_ads)} RSAs.")

    # --- Dry-run preview with breakdown
    if args.dry_run:
        total = len(src_keywords)
        negatives = 0
        dup_vs_dest = 0
        to_create = 0
        seen_normalized = set()  # avoid dup creates when forcing EXACT or mixing positives/negatives

        for r in src_keywords:
            c = r.ad_group_criterion
            text = c.keyword.text.strip().lower()
            mt_name = "EXACT" if args.only_exact else c.keyword.match_type.name
            is_negative = bool(c.negative)

            if is_negative and not args.copy_negatives:
                negatives += 1
                continue

            key_dest = (text, mt_name, is_negative)

            if key_dest in existing_kw:
                dup_vs_dest += 1
                continue

            # prevent duplicates within this run (e.g., same text in Broad+Phrase → both Exact)
            if key_dest in seen_normalized:
                dup_vs_dest += 1
                continue

            seen_normalized.add(key_dest)
            to_create += 1

        print("DRY RUN SUMMARY:")
        print(f"  Total source keywords: {total}")
        print(f"  Negatives skipped (no --copy-negatives): {negatives}" if not args.copy_negatives else
              f"  Negatives to consider: included")
        print(f"  Duplicates skipped vs destination/normalized: {dup_vs_dest}")
        print(f"  Would create: {to_create} keywords")
        # RSAs
        would_create_ads = 0
        for r in src_ads:
            ad = r.ad_group_ad.ad
            rsa = ad.responsive_search_ad
            if not rsa:
                continue
            h = tuple(sorted([a.text.strip() for a in rsa.headlines]))
            d = tuple(sorted([a.text.strip() for a in rsa.descriptions]))
            urls = tuple(sorted(ad.final_urls))
            path1 = rsa.path1
            path2 = rsa.path2
            fp = (h, d, urls, path1, path2)
            if fp not in existing_ads:
                would_create_ads += 1
        print(f"  Would create RSAs: {would_create_ads}")
        return

    # --- Mutations
    added_kw = create_keywords(
        client, args.customer_id, dest_ag_res, src_keywords, existing_kw,
        only_exact=args.only_exact, pause_on_create=args.pause_on_create,
        dedupe=(not args.no_dedupe), copy_negatives=args.copy_negatives
    )
    added_ads = create_rsas(
        client, args.customer_id, dest_ag_res, src_ads, existing_ads,
        pause_on_create=args.pause_on_create, dedupe=(not args.no_dedupe)
    )
    print(f"Created {added_kw} keywords and {added_ads} RSAs in destination.")


if __name__ == "__main__":
    main()
