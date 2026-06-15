import os

"""
SLB DELFI Data Pipeline Configuration Matrix
Centralizes environmental topology variables for Object Storage Tiers (S3/MinIO) 
and local project filesystem routing paths.
"""

# Simulated Cloud Infrastructure Gateway Node (MinIO/S3)
S3_ENDPOINT = "http://localhost:9000"
AWS_ACCESS_KEY = "slb_admin"
AWS_SECRET_KEY = "delfi_secret_2026"
BUCKET_NAME = "telemetry-data-lake"

# Local Filesystem Asset Path Routing Management
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

print(f"[CONFIG LOADED] Target Storage Node Gateway configured for endpoint: '{S3_ENDPOINT}'")
print(f"[CONFIG LOADED] Data directory established at: '{DATA_DIR}'")