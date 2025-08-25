#!/usr/bin/env python3
"""
ads_audit.py — Google Ads URL, RSA, and UTM audit

Requirements:
  pip install google-ads==21.0.0 requests tldextract

Auth:
  Configure ~/.google-ads.yaml (developer_token, oAuth, login_customer_id, etc.)

Usage:
  python ads_audit.py --customer-id 1234567890 --out ./out
  python ads_audit.py --customer-id 1234567890 --out ./out --check-http --timeout 5

Outputs:
  ./out/ads.csv                     # one row per ad
  ./out/rsa_assets.csv              # one row per RSA asset (headline/description)
  ./out/landing_pages.csv           # URL-level aggregation from landing_page_view (unexpanded)
  ./out/expanded_landing_pages.csv  # URL-level aggregation after redirects
  ./out/ad_url_map.csv              # ad_id → URL(s) crosswalk for UI lookups
  ./out/sitelink_urls.csv           # sitelink asset URLs by campaign/ad group
  ./out/findings.csv                # audit findings (one row per finding)
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from typing import Iterable, List, Dict, Any, Tuple, Optional
from urllib.parse import urlparse, parse_qs
import re

import requests
import tldextract
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


GAQL_ADS = """
SELECT
  customer.id,
  campaign.id, campaign.name, campaign.status,
  ad_group.id, ad_group.name, ad_group.status,
  ad_group_ad.ad.id,
  ad_group_ad.ad.name,
  ad_group_ad.ad.type,
  ad_group_ad.status,
  ad_group_ad.ad_strength,
  ad_group_ad.policy_summary.approval_status,
  ad_group_ad.ad.final_urls,
  ad_group_ad.ad.final_mobile_urls,
  ad_group_ad.ad.display_url,
  ad_group_ad.ad.tracking_url_template,
  ad_group_ad.ad.url_custom_parameters
FROM ad_group_ad
WHERE
  ad_group_ad.status = 'ENABLED'
  AND ad_group.status = 'ENABLED'
  AND campaign.status = 'ENABLED'
"""

GAQL_RSA_ASSETS = """
SELECT
  campaign.id,
  ad_group.id,
  ad_group_ad.ad.id,
  ad_group_ad.status,
  ad_group_ad_asset_view.field_type,
  ad_group_ad_asset_view.enabled,
  asset.text_asset.text,
  asset.policy_summary.approval_status
FROM ad_group_ad_asset_view
WHERE
  ad_group_ad.status = 'ENABLED'
  AND ad_group.status = 'ENABLED'
  AND campaign.status = 'ENABLED'
  AND ad_group_ad_asset_view.field_type IN ('HEADLINE','DESCRIPTION')
"""

GAQL_LANDING_PAGES = """
-- Unexpanded landing page views (aggregates by final URL)
SELECT
  customer.id,
  landing_page_view.unexpanded_final_url,
  metrics.clicks,
  metrics.impressions
FROM landing_page_view
WHERE segments.date DURING LAST_30_DAYS
"""

GAQL_EXPANDED_LANDING_PAGES = """
SELECT
  customer.id,
  expanded_landing_page_view.expanded_final_url,
  metrics.clicks,
  metrics.impressions
FROM expanded_landing_page_view
WHERE segments.date DURING LAST_30_DAYS
"""

# Sitelink URLs at both campaign and ad group levels
GAQL_SITELINKS = """
SELECT
  customer.id,
  asset.id,
  asset.name,
  asset.sitelink_asset.link_text,
  asset.sitelink_asset.final_urls,
  asset.sitelink_asset.final_mobile_urls,
  campaign.id,
  ad_group.id
FROM asset
LEFT JOIN campaign_asset ON campaign_asset.asset = asset.resource_name
LEFT JOIN ad_group_asset ON ad_group_asset.asset = asset.resource_name
WHERE asset.type = 'SITELINK'
"""


def ensure_out_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_csv(path: str, rows: Iterable[Dict[str, Any]], fieldnames: List[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            # stringify lists/dicts for CSV
            out = {}
            for k, v in r.items():
                if isinstance(v, (list, dict)):
                    out[k] = str(v)
                else:
                    out[k] = v
            w.writerow(out)


def norm_domain(url: str) -> Optional[str]:
    try:
        p = urlparse(url)
        if not p.netloc:
            return None
        ext = tldextract.extract(p.netloc)
        if not ext.domain:
            return p.netloc.lower()
        root = ".".join(part for part in [ext.domain, ext.suffix] if part)
        sub = ext.subdomain
        # return full host (sub + root) for exact matching
        host = ".".join([sub, root]) if sub else root
        return host.lower()
    except Exception:
        return None


def parse_params(url: str) -> Dict[str, List[str]]:
    try:
        return parse_qs(urlparse(url).query, keep_blank_values=True)
    except Exception:
        return {}


def is_https(url: str) -> bool:
    try:
        return urlparse(url).scheme.lower() == "https"
    except Exception:
        return False


def http_probe(url: str, timeout: int = 5) -> Tuple[Optional[int], Optional[str]]:
    try:
        # HEAD first, fallback to GET when servers block HEAD
        r = requests.head(url, allow_redirects=True, timeout=timeout)
        if r.status_code in (405, 403) and r.headers.get("allow", "").find("HEAD") == -1:
            r = requests.get(url, allow_redirects=True, timeout=timeout)
        return r.status_code, r.url
    except Exception as e:
        return None, str(e)


def fetch_stream(client: GoogleAdsClient, customer_id: str, query: str, api_version: str):
    ga_service = client.get_service("GoogleAdsService", version=api_version)
    stream = ga_service.search_stream(customer_id=customer_id, query=query)
    for batch in stream:
        for row in batch.results:
            yield row


def rows_ads(client: GoogleAdsClient, customer_id: str, api_version: str) -> List[Dict[str, Any]]:
    out = []
    for row in fetch_stream(client, customer_id, GAQL_ADS, api_version):
        ad = row.ad_group_ad.ad
        out.append({
            "customer_id": row.customer.id,
            "campaign_id": row.campaign.id,
            "campaign_name": row.campaign.name,
            "ad_group_id": row.ad_group.id,
            "ad_group_name": row.ad_group.name,
            "ad_id": ad.id,
            "ad_name": ad.name if getattr(ad, "name", None) else "",
            "ad_type": ad.type_.name if hasattr(ad.type_, "name") else str(ad.type_),
            "ad_status": row.ad_group_ad.status.name,
            "ad_strength": row.ad_group_ad.ad_strength.name if hasattr(row.ad_group_ad.ad_strength, "name") else str(row.ad_group_ad.ad_strength),
            "policy_status": row.ad_group_ad.policy_summary.approval_status.name,
            "final_urls": [u for u in ad.final_urls],
            "final_mobile_urls": [u for u in ad.final_mobile_urls],
            "display_url": ad.display_url if getattr(ad, "display_url", None) else "",
            "tracking_url_template": ad.tracking_url_template if getattr(ad, "tracking_url_template", None) else "",
            "url_custom_parameters": [{"key": p.key, "value": p.value} for p in ad.url_custom_parameters],
        })
    return out


def rows_ad_url_crosswalk(ads_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create one row per (ad_id, url, source) for easy lookups in UI."""
    x = []
    for r in ads_rows:
        for u in r.get("final_urls", []) or []:
            x.append({
                "ad_id": r["ad_id"],
                "campaign_id": r["campaign_id"],
                "ad_group_id": r["ad_group_id"],
                "url": u,
                "url_no_query": u.split("?", 1)[0],
                "source": "ad.final_urls",
            })
        for u in r.get("final_mobile_urls", []) or []:
            x.append({
                "ad_id": r["ad_id"],
                "campaign_id": r["campaign_id"],
                "ad_group_id": r["ad_group_id"],
                "url": u,
                "url_no_query": u.split("?", 1)[0],
                "source": "ad.final_mobile_urls",
            })
    return x


def rows_rsa_assets(client: GoogleAdsClient, customer_id: str, api_version: str) -> List[Dict[str, Any]]:
    out = []
    for row in fetch_stream(client, customer_id, GAQL_RSA_ASSETS, api_version):
        out.append({
            "campaign_id": row.campaign.id,
            "ad_group_id": row.ad_group.id,
            "ad_id": row.ad_group_ad.ad.id,
            "ad_status": row.ad_group_ad.status.name,
            "field_type": row.ad_group_ad_asset_view.field_type.name,
            "asset_enabled": row.ad_group_ad_asset_view.enabled,
            "text": row.asset.text_asset.text if getattr(row.asset, "text_asset", None) else "",
            "asset_policy_status": row.asset.policy_summary.approval_status.name if getattr(row.asset, "policy_summary", None) else "",
        })
    return out


def rows_landing_pages(client: GoogleAdsClient, customer_id: str, api_version: str) -> List[Dict[str, Any]]:
    out = []
    for row in fetch_stream(client, customer_id, GAQL_LANDING_PAGES, api_version):
        url = row.landing_page_view.unexpanded_final_url
        out.append({
            "customer_id": row.customer.id,
            "unexpanded_final_url": url,
            "clicks_last_30d": row.metrics.clicks,
            "impressions_last_30d": row.metrics.impressions,
        })
    return out


def rows_expanded_landing_pages(client: GoogleAdsClient, customer_id: str, api_version: str) -> List[Dict[str, Any]]:
    out = []
    for row in fetch_stream(client, customer_id, GAQL_EXPANDED_LANDING_PAGES, api_version):
        url = row.expanded_landing_page_view.expanded_final_url
        out.append({
            "customer_id": row.customer.id,
            "expanded_final_url": url,
            "clicks_last_30d": row.metrics.clicks,
            "impressions_last_30d": row.metrics.impressions,
        })
    return out


def rows_sitelinks(client: GoogleAdsClient, customer_id: str, api_version: str) -> List[Dict[str, Any]]:
    out = []
    for row in fetch_stream(client, customer_id, GAQL_SITELINKS, api_version):
        a = row.asset
        out.append({
            "customer_id": row.customer.id,
            "asset_id": a.id,
            "asset_name": getattr(a, "name", "") or "",
            "link_text": a.sitelink_asset.link_text if getattr(a, "sitelink_asset", None) else "",
            "final_urls": list(getattr(a.sitelink_asset, "final_urls", [])),
            "final_mobile_urls": list(getattr(a.sitelink_asset, "final_mobile_urls", [])),
            "campaign_id": row.campaign.id if getattr(row, "campaign", None) else "",
            "ad_group_id": row.ad_group.id if getattr(row, "ad_group", None) else "",
        })
    return out


def audit_findings(
    ads: List[Dict[str, Any]],
    check_http: bool,
    timeout: int,
    utm_required: List[str],
    utm_expect_exact: Dict[str, str],
    utm_expect_regex: Dict[str, str],
    utm_case: Optional[str],
    allow_autotag_only: bool,
) -> List[Dict[str, Any]]:
    findings = []
    for ad in ads:
        ad_id = ad["ad_id"]
        display_host = norm_domain(ad.get("display_url") or "") if ad.get("display_url") else None

        final_urls = ad.get("final_urls") or []
        mobile_urls = ad.get("final_mobile_urls") or []
        template = ad.get("tracking_url_template") or ""

        if not final_urls:
            findings.append({
                "ad_id": ad_id,
                "severity": "error",
                "issue": "No final_urls set",
                "detail": "",
            })

        if display_host:
            for u in final_urls:
                host = norm_domain(u)
                if host and host != display_host:
                    findings.append({
                        "ad_id": ad_id,
                        "severity": "warn",
                        "issue": "Domain mismatch",
                        "detail": f"display={display_host} final={host} ({u})",
                    })

        for u in final_urls:
            if not is_https(u):
                findings.append({
                    "ad_id": ad_id,
                    "severity": "warn",
                    "issue": "Non-HTTPS final URL",
                    "detail": u,
                })
            qs = parse_params(u)
            # Skip UTM checks when gclid present (optional)
            if allow_autotag_only and "gclid" in qs:
                pass
            else:
                # Required keys present?
                missing = [k for k in utm_required if k not in qs]
                if missing:
                    findings.append({
                        "ad_id": ad_id,
                        "severity": "warn",
                        "issue": "UTM missing",
                        "detail": f"{u} missing {','.join(missing)}",
                    })
                # Empty or duplicate values
                for k, vals in qs.items():
                    if k.startswith("utm_"):
                        if any(v == "" for v in vals):
                            findings.append({
                                "ad_id": ad_id,
                                "severity": "warn",
                                "issue": "UTM empty value",
                                "detail": f"{u} {k}=",
                            })
                        if len(vals) > 1:
                            findings.append({
                                "ad_id": ad_id,
                                "severity": "info",
                                "issue": "UTM duplicate parameter",
                                "detail": f"{u} {k} has {len(vals)} values",
                            })
                        if utm_case in ("lower", "upper"):
                            bad = [v for v in vals if (v != (v.lower() if utm_case == 'lower' else v.upper()))]
                            if bad:
                                findings.append({
                                    "ad_id": ad_id,
                                    "severity": "info",
                                    "issue": "UTM case policy",
                                    "detail": f"{u} {k} not {utm_case}",
                                })
                # Exact value expectations
                for k, expected in utm_expect_exact.items():
                    if k in qs:
                        val = qs[k][0]
                        if val != expected:
                            findings.append({
                                "ad_id": ad_id,
                                "severity": "warn",
                                "issue": "UTM mismatch (exact)",
                                "detail": f"{u} {k}='{val}' != '{expected}'",
                            })
                # Regex expectations
                for k, pattern in utm_expect_regex.items():
                    if k in qs:
                        val = qs[k][0]
                        if re.fullmatch(pattern, val) is None:
                            findings.append({
                                "ad_id": ad_id,
                                "severity": "warn",
                                "issue": "UTM mismatch (pattern)",
                                "detail": f"{u} {k}='{val}' !~ /{pattern}/",
                            })
            if check_http:
                code, note = http_probe(u, timeout=timeout)
                if code is None:
                    findings.append({
                        "ad_id": ad_id,
                        "severity": "error",
                        "issue": "HTTP check failed",
                        "detail": f"{u} error={note}",
                    })
                elif code >= 400:
                    findings.append({
                        "ad_id": ad_id,
                        "severity": "error",
                        "issue": "HTTP non-2xx",
                        "detail": f"{u} status={code}",
                    })

        if mobile_urls == [] and final_urls:
            findings.append({
                "ad_id": ad_id,
                "severity": "info",
                "issue": "No final_mobile_urls",
                "detail": "Consider mobile-specific URLs if site differs",
            })

        if template:
            # sanity: tracking templates usually contain {lpurl}
            if "{lpurl" not in template.lower():
                findings.append({
                    "ad_id": ad_id,
                    "severity": "warn",
                    "issue": "Tracking template missing {lpurl}",
                    "detail": template,
                })

    return findings


def main():
    parser = argparse.ArgumentParser(description="Audit enabled Google Ads URLs & RSA assets.")
    parser.add_argument("--customer-id", help="Customer ID (without dashes), e.g., 1234567890")
    parser.add_argument("--out", default="./out", help="Output directory")
    parser.add_argument("--api-version", default="v21",
                        help="Google Ads API version (e.g., v21)")
    parser.add_argument("--check-http", action="store_true", help="Probe final URLs via HTTP")
    parser.add_argument("--timeout", type=int, default=5, help="HTTP probe timeout (seconds)")
    parser.add_argument("--login-customer-id", help="Manager account (MCC) ID without dashes to use as login_customer_id")
    parser.add_argument("--list-accounts", action="store_true",
                        help="List account resource names and exit")
    parser.add_argument("--describe-accounts", action="store_true",
                        help="List account details (name, currency, tz, manager flag) and exit")
    # UTM enforcement
    parser.add_argument("--utm-required", nargs="*", default=["utm_source", "utm_medium", "utm_campaign"],
                        help="Space-separated required UTM keys")
    parser.add_argument("--utm-expect", action="append", default=[],
                        help="Exact expectation: key=value (repeatable)")
    parser.add_argument("--utm-match", action="append", default=[],
                        help="Regex expectation: key=/pattern/ (repeatable)")
    parser.add_argument("--utm-case", choices=["lower", "upper", "none"], default="none",
                        help="Enforce case for UTM values (default: none)")
    parser.add_argument("--allow-autotag-only", action="store_true",
                        help="If gclid present, skip UTM checks for that URL")
    args = parser.parse_args()

    ensure_out_dir(args.out)

    try:
        client = GoogleAdsClient.load_from_storage()
        if args.login_customer_id:
            client.login_customer_id = args.login_customer_id
    except Exception as e:
        print(f"Failed to load Google Ads config (~/.google-ads.yaml): {e}", file=sys.stderr)
        sys.exit(1)

    # If requested, list accounts and exit (no customer-id needed)
    if args.list_accounts:
        svc = client.get_service("CustomerService", version=args.api_version)
        res = svc.list_accessible_customers()
        print("# Accessible customer resource names:")
        for rn in res.resource_names:
            print(rn)  # e.g., 'customers/1234567890'
        return
    if args.describe_accounts:
        cust_svc = client.get_service("CustomerService", version=args.api_version)
        ga_svc = client.get_service("GoogleAdsService", version=args.api_version)
        res = cust_svc.list_accessible_customers()
        print("# Accounts:")
        for rn in res.resource_names:
            # rn like 'customers/1234567890' → CID:
            cid = rn.split("/")[1]
            # Fetch a few fields about the customer
            q = ("SELECT customer.id, customer.descriptive_name, "
                 "customer.currency_code, customer.time_zone, "
                 "customer.manager FROM customer LIMIT 1")
            try:
                for b in ga_svc.search_stream(customer_id=cid, query=q):
                    for row in b.results:
                        c = row.customer
                        print(f"{cid}\tname='{c.descriptive_name}'\t"
                              f"currency={c.currency_code}\ttz={c.time_zone}\t"
                              f"manager={c.manager}")
            except Exception as e:
                print(f"{cid}\t(error: {e})")
        return

    # From here on we require a customer id
    if not args.customer_id:
        print("--customer-id is required unless --list-accounts is used", file=sys.stderr)
        sys.exit(2)

    try:
        print("Fetching enabled ads ...", file=sys.stderr)
        ads = rows_ads(client, args.customer_id, args.api_version)
        print(f"  ads: {len(ads)}", file=sys.stderr)

        print("Fetching RSA assets ...", file=sys.stderr)
        rsa = rows_rsa_assets(client, args.customer_id, args.api_version)
        print(f"  assets: {len(rsa)}", file=sys.stderr)

        print("Fetching landing pages (last 30d) ...", file=sys.stderr)
        lps = rows_landing_pages(client, args.customer_id, args.api_version)
        print(f"  landing pages: {len(lps)}", file=sys.stderr)

        print("Fetching expanded landing pages (last 30d) ...", file=sys.stderr)
        try:
            elps = rows_expanded_landing_pages(client, args.customer_id, args.api_version)
            print(f"  expanded landing pages: {len(elps)}", file=sys.stderr)
        except Exception:
            elps = []
            print("  expanded landing pages: (not available)", file=sys.stderr)

        print("Fetching sitelinks ...", file=sys.stderr)
        sitelinks = rows_sitelinks(client, args.customer_id, args.api_version)
        print(f"  sitelink assets: {len(sitelinks)}", file=sys.stderr)

        print("Auditing URLs ...", file=sys.stderr)
        # Parse expectations into dicts
        expect_exact: Dict[str, str] = {}
        for item in args.utm_expect:
            if "=" in item:
                k, v = item.split("=", 1)
                expect_exact[k.strip()] = v.strip()
        expect_regex: Dict[str, str] = {}
        for item in args.utm_match:
            if "=" in item:
                k, v = item.split("=", 1)
                v = v.strip()
                if v.startswith("/") and v.endswith("/"):
                    v = v[1:-1]
                expect_regex[k.strip()] = v
        utm_case = None if args.utm_case == "none" else args.utm_case
        findings = audit_findings(
            ads,
            check_http=args.check_http,
            timeout=args.timeout,
            utm_required=args.utm_required,
            utm_expect_exact=expect_exact,
            utm_expect_regex=expect_regex,
            utm_case=utm_case,
            allow_autotag_only=args.allow_autotag_only,
        )
        print(f"  findings: {len(findings)}", file=sys.stderr)

        # Write CSVs
        write_csv(
            os.path.join(args.out, "ads.csv"),
            ads,
            [
                "customer_id","campaign_id","campaign_name","ad_group_id","ad_group_name",
                "ad_id","ad_name","ad_type","ad_status","ad_strength","policy_status",
                "final_urls","final_mobile_urls","display_url","tracking_url_template","url_custom_parameters"
            ],
        )
        write_csv(
            os.path.join(args.out, "rsa_assets.csv"),
            rsa,
            ["campaign_id","ad_group_id","ad_id","ad_status","field_type","asset_enabled","text","asset_policy_status"],
        )
        write_csv(
            os.path.join(args.out, "landing_pages.csv"),
            lps,
            ["customer_id","unexpanded_final_url","clicks_last_30d","impressions_last_30d"],
        )
        if elps:
            write_csv(
                os.path.join(args.out, "expanded_landing_pages.csv"),
                elps,
                ["customer_id","expanded_final_url","clicks_last_30d","impressions_last_30d"],
            )
        cross = rows_ad_url_crosswalk(ads)
        write_csv(
            os.path.join(args.out, "ad_url_map.csv"),
            cross,
            ["ad_id","campaign_id","ad_group_id","url","url_no_query","source"],
        )
        write_csv(
            os.path.join(args.out, "sitelink_urls.csv"),
            sitelinks,
            ["customer_id","asset_id","asset_name","link_text","final_urls","final_mobile_urls","campaign_id","ad_group_id"],
        )
        write_csv(
            os.path.join(args.out, "findings.csv"),
            findings,
            ["ad_id","severity","issue","detail"],
        )

        print(f"Done. Files in: {os.path.abspath(args.out)}", file=sys.stderr)

    except GoogleAdsException as ex:
        print(f"GoogleAdsException: {ex.error.code().name if ex.error else ''}", file=sys.stderr)
        for e in ex.failure.errors:
            print(f"  - {e.error_code}: {e.message}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    t0 = time.time()
    try:
        main()
    finally:
        dt = time.time() - t0
        print(f"Elapsed: {dt:.1f}s", file=sys.stderr)
