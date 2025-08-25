#!/usr/bin/env python3
from google.ads.googleads.client import GoogleAdsClient

client = GoogleAdsClient.load_from_storage()

# 1) Show manager(s) your user can access
cust_svc = client.get_service("CustomerService")
resp = cust_svc.list_accessible_customers()
print("Accessible manager/customer resource names:")
for rn in resp.resource_names:
    print(" -", rn)  # e.g., customers/1234567890

# 2) If you set login_customer_id, enumerate its hierarchy
try:
    login_id = client.login_customer_id
    if login_id:
        ga = client.get_service("GoogleAdsService")
        q = """
          SELECT
            customer_client.client_customer,
            customer_client.level,
            customer_client.descriptive_name,
            customer_client.hidden
          FROM customer_client
          WHERE customer_client.level <= 1
        """
        print(f"\nHierarchy under login_customer_id={login_id}:")
        for row in ga.search(customer_id=str(login_id), query=q):
            cid = row.customer_client.client_customer.split("/")[-1]
            print(f" - {cid} | level={row.customer_client.level} | name={row.customer_client.descriptive_name} | hidden={row.customer_client.hidden}")
except Exception as e:
    print("\n(Note) Could not list hierarchy. Error:", e)
