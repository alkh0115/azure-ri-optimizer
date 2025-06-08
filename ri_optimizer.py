import os
import subprocess
import json
import requests
import pandas as pd
from datetime import datetime

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

def get_token():
    print("Getting Azure access token using az CLI...")
    result = subprocess.run(
        [r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd", "account", "get-access-token", "--resource", "https://management.azure.com/"],
        capture_output=True, text=True
    )
    token_json = json.loads(result.stdout)
    return token_json["accessToken"]

def get_reservations(token):
    print("Getting Reserved Instance data...")
    url = f"https://management.azure.com/providers/Microsoft.Capacity/reservationOrders?api-version=2022-03-01"
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(url, headers=headers).json()

def get_savings_plans(token):
    print("Getting Savings Plans data...")
    url = f"https://management.azure.com/providers/Microsoft.Consumption/savingsPlans?api-version=2022-10-01"
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(url, headers=headers).json()

def get_savings_plans_utilization(token, sp_id):
    print(f"Getting Savings Plan utilization for {sp_id}...")
    url = f"https://management.azure.com{sp_id}/usages?api-version=2022-10-01"
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(url, headers=headers).json()

def generate_ri_recommendations():
    print("Running generate_ri_recommendations()")

    token = get_token()
    print("Token acquired successfully")

    report_data = []

    # Reserved Instances
    ri_data = get_reservations(token)
    for order in ri_data.get("value", []):
        usage_url = f"https://management.azure.com{order['id']}/usages?api-version=2022-03-01"
        usage = requests.get(usage_url, headers={"Authorization": f"Bearer {token}"}).json()
        for item in usage.get("value", []):
            utilization = item.get("utilizationPercentage", 100)
            if utilization < 70:
                report_data.append({
                    "type": "Reserved Instance",
                    "name": item["name"],
                    "utilization": utilization,
                    "scope": item["properties"].get("scopeId", "unknown"),
                    "recommendation": "Consider SKU change or reassignment"
                })

    # Savings Plans
    sp_data = get_savings_plans(token)
    for sp in sp_data.get("value", []):
        usage_data = get_savings_plans_utilization(token, sp["id"])
        for usage_item in usage_data.get("value", []):
            utilization = usage_item.get("utilizationPercentage", 100)
            if utilization < 70:
                report_data.append({
                    "type": "Savings Plan",
                    "name": sp["name"],
                    "utilization": utilization,
                    "scope": usage_item["properties"].get("scope", "unknown"),
                    "recommendation": "Investigate workloads; consider changes"
                })

    df = pd.DataFrame(report_data)
    filename = f"./ri_sp_report_{datetime.now().strftime('%Y%m%d')}.csv"
    df.to_csv(filename, index=False)
    print(f"Saved report to: {filename}")
