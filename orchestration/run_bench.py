import subprocess
import time
import json
import re

DATABASE = "fisheries_db_diego"
OUTPUT_LOC = "s3://big-data-project-gang-582465846893/athena-results/"

QUERIES = [
    ("Q1", "CSV", "SELECT year, SUM(CAST(tonnes AS DOUBLE)) AS total_tonnes FROM global_raw GROUP BY year ORDER BY year;"),
    ("Q1", "Parquet", "SELECT year, SUM(CAST(tonnes AS DOUBLE)) AS total_tonnes FROM global_processed GROUP BY year ORDER BY year;"),
    ("Q2", "CSV", "SELECT fishing_entity, SUM(CAST(tonnes AS DOUBLE)) AS total_tonnes FROM global_raw WHERE year = '2010' GROUP BY fishing_entity ORDER BY total_tonnes DESC LIMIT 5;"),
    ("Q2", "Parquet", "SELECT fishing_entity, SUM(CAST(tonnes AS DOUBLE)) AS total_tonnes FROM global_processed WHERE year = '2010' GROUP BY fishing_entity ORDER BY total_tonnes DESC LIMIT 5;"),
    ("Q3", "CSV", "SELECT fishing_sector, catch_type, reporting_status, COUNT(*) AS registros, SUM(CAST(tonnes AS DOUBLE)) AS total_tonnes FROM eez_raw WHERE CAST(year AS INTEGER) BETWEEN 2000 AND 2018 GROUP BY fishing_sector, catch_type, reporting_status ORDER BY total_tonnes DESC;"),
    ("Q3", "Parquet", "SELECT fishing_sector, catch_type, reporting_status, COUNT(*) AS registros, SUM(CAST(tonnes AS DOUBLE)) AS total_tonnes FROM eez_processed WHERE CAST(year AS INTEGER) BETWEEN 2000 AND 2018 GROUP BY fishing_sector, catch_type, reporting_status ORDER BY total_tonnes DESC;")
]

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error ejecutando: {cmd}\n{result.stderr}")
        return None
    return result.stdout.strip()

print("Ejecutando Benchmark en Athena (6 queries)...")
results_data = {}

for q_id, q_format, query in QUERIES:
    print(f"Ejecutando {q_id} ({q_format})...")
    exec_id = run_cmd(f'aws athena start-query-execution --query-string "{query}" --query-execution-context Database={DATABASE} --result-configuration OutputLocation={OUTPUT_LOC} --query QueryExecutionId --output text')
    
    while True:
        status = run_cmd(f"aws athena get-query-execution --query-execution-id {exec_id} --query QueryExecution.Status.State --output text")
        if status in ["SUCCEEDED", "FAILED", "CANCELLED"]:
            break
        time.sleep(1)
    
    if status == "SUCCEEDED":
        stats_json = run_cmd(f"aws athena get-query-execution --query-execution-id {exec_id} --query QueryExecution.Statistics --output json")
        stats = json.loads(stats_json)
        time_ms = stats.get("EngineExecutionTimeInMillis", 0)
        bytes_scanned = stats.get("DataScannedInBytes", 0)
        
        time_s = time_ms / 1000.0
        mb_scanned = bytes_scanned / (1024 * 1024)
        
        results_data[f"{q_id}_{q_format}"] = {"time": f"{time_s:.2f}s", "bytes": f"{mb_scanned:.2f} MB"}
        print(f"-> {time_s:.2f}s, {mb_scanned:.2f} MB")
    else:
        err = run_cmd(f"aws athena get-query-execution --query-execution-id {exec_id} --query QueryExecution.Status.StateChangeReason --output text")
        print(f"-> Fallo: {err}")
        results_data[f"{q_id}_{q_format}"] = {"time": "ERROR", "bytes": "ERROR"}

print("=======================================")
for key, data in results_data.items():
    print(f"{key}|{data['time']}|{data['bytes']}")
