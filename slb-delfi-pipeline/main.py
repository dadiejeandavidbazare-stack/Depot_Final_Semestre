import os
import pandas as pd
import boto3
from io import BytesIO
from config.settings import S3_ENDPOINT, AWS_ACCESS_KEY, AWS_SECRET_KEY, BUCKET_NAME, DATA_DIR
from src.transformer import clean_and_process_telemetry

def initialize_s3_client():
    """Initializes and returns a secure storage client link for the S3 Object Storage tier."""
    return boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

def main():
    print("🚀 [SLB PIPELINE] Initializing OSDU/DELFI Compliant data lifecycle processing...")
    
    input_file = os.path.join(DATA_DIR, "raw_well_data.csv")
    if not os.path.exists(input_file):
        print(f"❌ CRITICAL ERROR: Target telemetry data payload missing at path: '{input_file}'. Please place your Volve data source there.")
        return

    # Optimized memory-ingestion layer (Explicit downhole sensor column datatype mapping)
    dtypes = {
        'WELL_BORE_CODE': 'category',
        'AVG_DOWNHOLE_PRESSURE': 'float32',
        'AVG_DOWNHOLE_TEMPERATURE': 'float32',
        'BORE_OIL_VOL': 'float32',
        'BORE_WAT_VOL': 'float32'
    }
    
    print("📥 Ingesting raw asset telemetry data stream...")
    try:
        # INFRASTRUCTURE ADJUSTMENT: Added thousands=' ' separator to safely parse spaces within large hydrocarbon volume metrics
        df_raw = pd.read_csv(
            input_file, 
            sep=';', 
            parse_dates=['DATEPRD'], 
            dtype=dtypes, 
            encoding='ISO-8859-1',
            decimal=',',
            thousands=' '
        )
    except Exception as ingestion_error:
        print(f"❌ CRITICAL ERROR: Data discovery ingestion phase aborted. Context: {ingestion_error}")
        return
    
    # Transformation Layer & Reservoir Business Rules Application
    print("⚙️ Initiating multi-variate sensor data cleansing and Water Cut KPI computation...")
    df_processed = clean_and_process_telemetry(df_raw)
    
    # Memory-Optimized High-Performance Columnar Serialization (Apache Parquet with Snappy)
    print("📦 Serializing processed core entity schema into highly optimized Apache Parquet format...")
    parquet_buffer = BytesIO()
    df_processed.to_parquet(parquet_buffer, index=False, compression='snappy')
    parquet_buffer.seek(0)
    
    # Distributed Data Lake Integration Layer (Local MinIO Instance)
    print("☁️ Establishing secure gateway protocol link to local S3 Data Lake node...")
    s3_client = initialize_s3_client()
    
    # Automated remote cloud storage bucket initialization layer
    try:
        s3_client.create_bucket(Bucket=BUCKET_NAME)
    except s3_client.exceptions.BucketAlreadyExists:
        pass
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        pass

    # Secure object streaming push utilizing structured time-series partition keys (year=2026)
    s3_key = "production/year=2026/well_telemetry.parquet"
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=parquet_buffer.getvalue()
    )
    
    print(f"✅ [PIPELINE SUCCESS] Data ingestion cycle complete. Asset structured layer safely stored under: {BUCKET_NAME}/{s3_key}")

if __name__ == "__main__":
    main()