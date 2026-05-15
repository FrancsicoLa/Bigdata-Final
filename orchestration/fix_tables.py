import subprocess
import time

DATABASE = "fisheries_db_diego"
OUTPUT_LOC = "s3://big-data-project-gang-582465846893/athena-results/"
BUCKET = "s3://big-data-project-gang-582465846893"

QUERIES = [
    # DROP existing
    "DROP TABLE IF EXISTS global_raw;",
    "DROP TABLE IF EXISTS global_processed;",
    "DROP TABLE IF EXISTS eez_raw;",
    "DROP TABLE IF EXISTS eez_processed;",
    "DROP TABLE IF EXISTS processed;",
    
    # CREATE global_raw
    f"""
    CREATE EXTERNAL TABLE `global_raw`(
      `year` string, 
      `fishing_entity` string, 
      `fishing_sector` string, 
      `catch_type` string, 
      `reporting_status` string, 
      `gear_type` string, 
      `end_use_type` string, 
      `tonnes` string, 
      `landed_value` string)
    ROW FORMAT DELIMITED 
      FIELDS TERMINATED BY ',' 
    LOCATION '{BUCKET}/raw/global/'
    TBLPROPERTIES ('skip.header.line.count'='1');
    """,
    
    # CREATE global_processed
    f"""
    CREATE EXTERNAL TABLE `global_processed`(
      `fishing_entity` string, 
      `fishing_sector` string, 
      `catch_type` string, 
      `reporting_status` string, 
      `gear_type` string, 
      `end_use_type` string, 
      `tonnes` string, 
      `landed_value` string)
    PARTITIONED BY (`year` string)
    STORED AS PARQUET
    LOCATION '{BUCKET}/processed/global/';
    """,
    
    # REPAIR global_processed
    "MSCK REPAIR TABLE `global_processed`;",
    
    # CREATE eez_raw
    f"""
    CREATE EXTERNAL TABLE `eez_raw`(
      `area_name` string,
      `area_type` string,
      `data_layer` string,
      `uncertainty_score` string,
      `year` string,
      `scientific_name` string,
      `common_name` string,
      `functional_group` string,
      `commercial_group` string,
      `fishing_entity` string,
      `fishing_sector` string,
      `catch_type` string,
      `reporting_status` string,
      `gear_type` string,
      `end_use_type` string,
      `tonnes` string,
      `landed_value` string)
    ROW FORMAT DELIMITED 
      FIELDS TERMINATED BY ',' 
    LOCATION '{BUCKET}/raw/eez/'
    TBLPROPERTIES ('skip.header.line.count'='1');
    """,
    
    # CREATE eez_processed
    f"""
    CREATE EXTERNAL TABLE `eez_processed`(
      `area_name` string,
      `area_type` string,
      `data_layer` string,
      `uncertainty_score` string,
      `scientific_name` string,
      `common_name` string,
      `functional_group` string,
      `commercial_group` string,
      `fishing_entity` string,
      `fishing_sector` string,
      `catch_type` string,
      `reporting_status` string,
      `gear_type` string,
      `end_use_type` string,
      `tonnes` string,
      `landed_value` string)
    PARTITIONED BY (`year` string)
    STORED AS PARQUET
    LOCATION '{BUCKET}/processed/eez/';
    """,
    
    # REPAIR eez_processed
    "MSCK REPAIR TABLE `eez_processed`;"
]

def run_athena(query):
    query = query.replace('\n', ' ')
    cmd = f'aws athena start-query-execution --query-string "{query}" --query-execution-context Database={DATABASE} --result-configuration OutputLocation={OUTPUT_LOC} --query QueryExecutionId --output text'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error starting query: {result.stderr}")
        return None
    exec_id = result.stdout.strip()
    
    while True:
        status = subprocess.run(f"aws athena get-query-execution --query-execution-id {exec_id} --query QueryExecution.Status.State --output text", shell=True, capture_output=True, text=True).stdout.strip()
        if status in ["SUCCEEDED", "FAILED", "CANCELLED"]:
            break
        time.sleep(1)
        
    if status == "FAILED":
        err = subprocess.run(f"aws athena get-query-execution --query-execution-id {exec_id} --query QueryExecution.Status.StateChangeReason --output text", shell=True, capture_output=True, text=True).stdout.strip()
        print(f"Failed query: {err}")
    return status

print("Corrigiendo tablas en Athena...")
for q in QUERIES:
    print(f"Ejecutando: {q[:50]}...")
    run_athena(q)
print("¡Tablas corregidas!")
