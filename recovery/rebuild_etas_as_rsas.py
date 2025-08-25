#!/usr/bin/env python3
"""
Rebuild legacy Expanded Text Ads (ETAs) as Responsive Search Ads (RSAs).

- Default: ETA-like pinning (H1/H2/H3, D1/D2) unless --no-pin is used.
- New: --pad-mode {skip,generic}
    skip    -> only rebuild ETAs that already have >=3 headlines and >=2 descriptions (default)
    generic -> pad missing headlines/descriptions with unique, safe filler lines
- Dedupe vs existing RSAs (same text set, paths, URLs).
"""

import argparse
from google.ads.googleads.client import GoogleAdsClient


def ga(client):
    return client.get_service("GoogleAdsService")


def qrows(client, customer_id: str, query: str):
    return list(ga(client).search(customer_id=customer_id, query=query))


def get_dest_rsa_fingerprints(client, customer_id, ad_group_id):
    query = f"""
      SELECT
        ad_group_ad.ad.responsive_search_ad.headlines,
        ad_group_ad.ad.responsive_search_ad.descriptions,
        ad_group_ad.ad.responsive_search_ad.path1,
        ad_group_ad.ad.responsive_search_ad.path2,
        ad_group_ad.ad.final_urls
      FROM ad_group_ad
      WHERE ad_group_ad.ad_group = 'customers/{customer_id}/adGroups/{ad_group_id}'
        AND ad_group_ad.ad.type = RESPONSIVE_SEARCH_AD
    """
    fps = set()
    for r in qrows(client, customer_id, query):
        ad = r.ad_group_ad.ad
        rsa = ad.responsive_search_ad
        if not rsa:
            continue
        h = tuple(sorted([a.text.strip() for a in rsa.headlines]))
        d = tuple(sorted([a.text.strip() for a in rsa.descriptions]))
        urls = tuple(sorted(ad.final_urls))
        fps.add((h, d, urls, rsa.path1, rsa.path2))
    return fps


def get_etas(client, customer_id, source_ad_group_id):
    query = f"""
      SELECT
        ad_group_ad.status,
        ad_group_ad.ad.final_urls,
        ad_group_ad.ad.expanded_text_ad.headline_part1,
        ad_group_ad.ad.expanded_text_ad.headline_part2,
        ad_group_ad.ad.expanded_text_ad.headline_part3,
        ad_group_ad.ad.expanded_text_ad.description,
        ad_group_ad.ad.expanded_text_ad.description2,
        ad_group_ad.ad.expanded_text_ad.path1,
        ad_group_ad.ad.expanded_text_ad.path2
      FROM ad_group_ad
      WHERE ad_group_ad.ad_group = 'customers/{customer_id}/adGroups/{source_ad_group_id}'
        AND ad_group_ad.ad.type = EXPANDED_TEXT_AD
    """
    return qrows(client, customer_id, query)


# ---------- helpers ----------

FALLBACK_H = [
    "Accredited Online School",
    "Flexible, Self-Paced Program",
    "Enroll Online Today",
    "Tuition Options Available",
    "Trusted Since 2009",
    "Start Any Time",
]

FALLBACK_D = [
    "Finish at your pace with 100% online classes.",
    "Individualized support. Transfer credits accepted.",
    "Fully online. Enroll in minutes. Talk to Admissions.",
    "Accredited curriculum with flexible scheduling.",
]


def _text_asset(client, text, pin_field=None, no_pin=False):
    a = client.get_type("AdTextAsset")
    a.text = text
    if (pin_field is not None) and (not no_pin):
        a.pinned_field = pin_field
    return a


def _unique_append(target_list, text_set, asset):
    """Append only if this exact text isn't present already (avoid DUPLICATE_ASSET)."""
    t = asset.text.strip()
    if t and t not in text_set:
        target_list.append(asset)
        text_set.add(t)


def ensure_min_assets_with_mode(client, headlines, descriptions, no_pin, pin_fields, pad_mode):
    """
    Enforce RSA minimums:
      - headlines >= 3
      - descriptions >= 2
    pad_mode:
      - 'skip'    -> do nothing (caller should skip if < mins)
      - 'generic' -> add unique fallback assets until mins are reached
    """
    if pad_mode != "generic":
        return  # nothing to do; caller will skip if short

    existing_h = {h.text.strip() for h in headlines}
    existing_d = {d.text.strip() for d in descriptions}

    # Headlines
    for fb in FALLBACK_H:
        if len(headlines) >= 3:
            break
        _unique_append(headlines, existing_h, _text_asset(client, fb, None, no_pin=True))

    # Descriptions
    for fb in FALLBACK_D:
        if len(descriptions) >= 2:
            break
        _unique_append(descriptions, existing_d, _text_asset(client, fb, None, no_pin=True))


def create_rsas_from_etas(
    client,
    customer_id,
    dest_ad_group_id,
    eta_rows,
    existing_fps,
    pause_on_create=False,
    preview=False,
    no_pin=False,
    pad_mode="skip",
):
    svc = client.get_service("AdGroupAdService")
    AdGroupAdStatusEnum = client.enums.AdGroupAdStatusEnum
    PinnedFieldEnum = client.enums.ServedAssetFieldTypeEnum

    pin_fields = {
        "HEADLINE_1": PinnedFieldEnum.HEADLINE_1,
        "HEADLINE_2": PinnedFieldEnum.HEADLINE_2,
        "HEADLINE_3": PinnedFieldEnum.HEADLINE_3,
        "DESCRIPTION_1": PinnedFieldEnum.DESCRIPTION_1,
        "DESCRIPTION_2": PinnedFieldEnum.DESCRIPTION_2,
    }

    def rsa_fp(heads, descs, urls, path1, path2):
        h = tuple(sorted([h.text.strip() for h in heads]))
        d = tuple(sorted([d.text.strip() for d in descs]))
        u = tuple(sorted(urls))
        return (h, d, u, path1, path2)

    ops = []
    would_create = 0
    skipped_short = 0

    for r in eta_rows:
        ad = r.ad_group_ad.ad
        eta = ad.expanded_text_ad
        if not eta:
            continue

        headlines, descriptions = [], []

        def add_head(text, pin_key=None):
            if text:
                pin = pin_fields[pin_key] if pin_key else None
                headlines.append(_text_asset(client, text, pin, no_pin=no_pin))

        def add_desc(text, pin_key=None):
            if text:
                pin = pin_fields[pin_key] if pin_key else None
                descriptions.append(_text_asset(client, text, pin, no_pin=no_pin))

        # Map ETA parts
        add_head(eta.headline_part1, "HEADLINE_1")
        add_head(eta.headline_part2, "HEADLINE_2")
        add_head(getattr(eta, "headline_part3", None), "HEADLINE_3")
        add_desc(eta.description, "DESCRIPTION_1")
        add_desc(getattr(eta, "description2", None), "DESCRIPTION_2")

        path1 = getattr(eta, "path1", None)
        path2 = getattr(eta, "path2", None)
        urls = list(ad.final_urls) if ad.final_urls else []

        # Must have at least some content & final URL
        if not headlines or not descriptions or not urls:
            skipped_short += 1
            continue

        # If we don't meet mins, either skip or pad with generic
        if len(headlines) < 3 or len(descriptions) < 2:
            if pad_mode == "skip":
                skipped_short += 1
                continue
            else:
                ensure_min_assets_with_mode(client, headlines, descriptions, no_pin, pin_fields, pad_mode)

        # De-dup texts within each ad (avoid duplicate asset error)
        seen_h, dedup_h = set(), []
        for h in headlines:
            t = h.text.strip()
            if t and t not in seen_h:
                dedup_h.append(h); seen_h.add(t)
        headlines = dedup_h

        seen_d, dedup_d = set(), []
        for d in descriptions:
            t = d.text.strip()
            if t and t not in seen_d:
                dedup_d.append(d); seen_d.add(t)
        descriptions = dedup_d

        # Final guard: must now meet RSA mins
        if len(headlines) < 3 or len(descriptions) < 2:
            skipped_short += 1
            continue

        fp = rsa_fp(headlines, descriptions, urls, path1, path2)
        if fp in existing_fps:
            continue

        if preview:
            would_create += 1
            continue

        op = client.get_type("AdGroupAdOperation")
        aga = op.create
        aga.ad_group = f"customers/{customer_id}/adGroups/{dest_ad_group_id}"
        aga.status = AdGroupAdStatusEnum.PAUSED if pause_on_create else AdGroupAdStatusEnum.ENABLED
        new_ad = aga.ad
        new_ad.final_urls.extend(urls)
        rsa = new_ad.responsive_search_ad
        rsa.headlines.extend(headlines)
        rsa.descriptions.extend(descriptions)
        if path1: rsa.path1 = path1
        if path2: rsa.path2 = path2
        ops.append(op)

    if preview:
        print(f"(info) skipped_incomplete={skipped_short} (pad_mode={pad_mode})")
        return would_create

    if ops:
        svc.mutate_ad_group_ads(customer_id=customer_id, operations=ops)

    print(f"(info) skipped_incomplete={skipped_short} (pad_mode={pad_mode})")
    return len(ops)


def resolve_name(client, customer_id, ad_group_id):
    q = f"""
      SELECT ad_group.name, campaign.name, ad_group.status
      FROM ad_group
      WHERE ad_group.id = {ad_group_id}
      LIMIT 1
    """
    rows = qrows(client, customer_id, q)
    if not rows:
        return (f"ad_group:{ad_group_id}", "campaign:?", "UNKNOWN")
    r = rows[0]
    return (r.ad_group.name, r.campaign.name, r.ad_group.status.name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--customer-id", required=True)
    ap.add_argument("--source-ad-group-id", required=True)
    ap.add_argument("--dest-ad-group-id", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pause-on-create", action="store_true")
    ap.add_argument("--no-pin", action="store_true", help="Do not pin assets; create normal RSAs.")
    ap.add_argument("--pad-mode", choices=["skip", "generic"], default="skip",
                    help="How to reach RSA minimums if ETA lacks assets (default: skip).")
    args = ap.parse_args()

    client = GoogleAdsClient.load_from_storage()

    sname, scamp, sstatus = resolve_name(client, args.customer_id, args.source_ad_group_id)
    dname, dcamp, dstatus = resolve_name(client, args.customer_id, args.dest_ad_group_id)
    print(f"Source ad group: {sname} (status={sstatus}) in campaign '{scamp}'")
    print(f"Destination ad group: {dname} (status={dstatus}) in campaign '{dcamp}'")

    etas = get_etas(client, args.customer_id, args.source_ad_group_id)
    print(f"Found {len(etas)} ETAs in source.")

    existing = get_dest_rsa_fingerprints(client, args.customer_id, args.dest_ad_group_id)

    if args.dry_run:
        would = create_rsas_from_etas(
            client, args.customer_id, args.dest_ad_group_id,
            etas, existing, pause_on_create=args.pause_on_create,
            preview=True, no_pin=args.no_pin, pad_mode=args.pad_mode
        )
        print(f"DRY RUN: would create {would} RSAs from ETAs.")
        return

    created = create_rsas_from_etas(
        client, args.customer_id, args.dest_ad_group_id,
        etas, existing, pause_on_create=args.pause_on_create,
        preview=False, no_pin=args.no_pin, pad_mode=args.pad_mode
    )
    print(f"Created {created} RSAs from ETAs in destination.")


if __name__ == "__main__":
    main()
