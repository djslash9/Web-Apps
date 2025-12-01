import json
import os
import pandas as pd
from datetime import datetime

DATA_FILE = "data/clients.json"

def ensure_data_file():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)

def load_data():
    ensure_data_file()
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_data(data):
    ensure_data_file()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_client_record(record):
    data = load_data()
    # Add a unique ID and timestamp if not present
    if "id" not in record:
        record["id"] = datetime.now().strftime("%Y%m%d%H%M%S%f")
    if "created_at" not in record:
        record["created_at"] = datetime.now().isoformat()
    
    data.append(record)
    save_data(data)

def update_client_record(updated_record):
    data = load_data()
    for i, record in enumerate(data):
        if record.get("id") == updated_record.get("id"):
            data[i] = updated_record
            break
    save_data(data)

def delete_client_record(record_id):
    data = load_data()
    data = [r for r in data if r.get("id") != record_id]
    save_data(data)

def get_all_organizations():
    data = load_data()
    return list(set([r.get("organization") for r in data if "organization" in r]))

def get_brands_for_org(org_name):
    data = load_data()
    brands = []
    for r in data:
        if r.get("organization") == org_name:
            brands.extend([b["name"] for b in r.get("brands", [])])
def get_record_by_org(org_name):
    data = load_data()
    for r in data:
        if r.get("organization") == org_name:
            return r
    return None
