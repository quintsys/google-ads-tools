#!/usr/bin/env python3
from google.ads.googleads.client import GoogleAdsClient

TARGET = "2091137189"

client = GoogleAdsClient.load_from_storage()
ga = client.get_service("GoogleAdsService")

def list_children(parent_id: str):
    q = """
      SELECT
        customer_client.client_customer,
        customer_client.descriptive_name,
        customer_client.level,
        customer_client.hidden
      FROM customer_client
      WHERE customer_client.level <= 1
    """
    print(f"\nUnder manager/customer {parent_id}:")
    found = False
    for row in ga.search(customer_id=parent_id, query=q):
        cid = row.customer_client.client_customer.split("/")[-1]
        name = row.customer_client.descriptive_name
        lvl = row.customer_client.level
        hidden = row.customer_client.hidden
        print(f" - {cid} | level={lvl} | hidden={hidden} | name={name}")
        if cid == TARGET:
            found = True
    if found:
        print(f"\n✅ FOUND target {TARGET} under {parent_id}")
    return found

# Start from the "accessible" roots we printed before
roots = ["2975516290","8630268244","9369249870"]
found_any = False
for rid in roots:
    try:
        if list_children(rid):
            found_any = True
    except Exception as e:
        print(f"(note) Could not enumerate under {rid}: {e}")

if not found_any:
    print("\n❌ Target not found under any root. Likely the OAuth user isn’t linked to that client.")
