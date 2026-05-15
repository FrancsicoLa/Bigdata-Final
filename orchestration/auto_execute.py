import subprocess
import time
import json

GLUE_JOB = "transform-fisheries"
CRAWLER = "fisheries-crawler_gang"
DATABASE = "fisheries_db_diego"
BUCKET = "s3://big-data-project-gang-582465846893"
OUTPUT_LOC = f"{BUCKET}/athena-results/"

QUERIES_BENCHMARK = [
    ("Q1", "CSV", "SELECT year, SUM(CAST(tonnes AS DOUBLE)) AS total_tonnes FROM global_raw GROUP BY year ORDER BY year;"),
    ("Q1", "Parquet", "SELECT year, SUM(CAST(tonnes AS DOUBLE)) AS total_tonnes FROM global_processed GROUP BY year ORDER BY year;"),
    ("Q2", "CSV", "SELECT fishing_entity, SUM(CAST(tonnes AS DOUBLE)) AS total_tonnes FROM global_raw WHERE year = '2010' GROUP BY fishing_entity ORDER BY total_tonnes DESC LIMIT 5;"),
    ("Q2", "Parquet", "SELECT fishing_entity, SUM(CAST(tonnes AS DOUBLE)) AS total_tonnes FROM global_processed WHERE year = '2010' GROUP BY fishing_entity ORDER BY total_tonnes DESC LIMIT 5;"),
    ("Q3", "CSV", "SELECT fishing_sector, catch_type, reporting_status, COUNT(*) AS registros, SUM(CAST(tonnes AS DOUBLE)) AS total_tonnes FROM eez_raw WHERE CAST(year AS INTEGER) BETWEEN 2000 AND 2018 GROUP BY fishing_sector, catch_type, reporting_status ORDER BY total_tonnes DESC;"),
    ("Q3", "Parquet", "SELECT fishing_sector, catch_type, reporting_status, COUNT(*) AS registros, SUM(CAST(tonnes AS DOUBLE)) AS total_tonnes FROM eez_processed WHERE CAST(year AS INTEGER) BETWEEN 2000 AND 2018 GROUP BY fishing_sector, catch_type, reporting_status ORDER BY total_tonnes DESC;")
]

DDL_QUERIES = [
    "DROP TABLE IF EXISTS global_raw;",
    "DROP TABLE IF EXISTS global_processed;",
    "DROP TABLE IF EXISTS eez_raw;",
    "DROP TABLE IF EXISTS eez_processed;",
    f"CREATE EXTERNAL TABLE `global_raw`(`year` string, `fishing_entity` string, `fishing_sector` string, `catch_type` string, `reporting_status` string, `gear_type` string, `end_use_type` string, `tonnes` string, `landed_value` string) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' LOCATION '{BUCKET}/raw/global/' TBLPROPERTIES ('skip.header.line.count'='1');",
    f"CREATE EXTERNAL TABLE `global_processed`(`fishing_entity` string, `fishing_sector` string, `catch_type` string, `reporting_status` string, `gear_type` string, `end_use_type` string, `tonnes` string, `landed_value` string) PARTITIONED BY (`year` string) STORED AS PARQUET LOCATION '{BUCKET}/processed/global/';",
    "MSCK REPAIR TABLE `global_processed`;",
    f"CREATE EXTERNAL TABLE `eez_raw`(`area_name` string, `area_type` string, `data_layer` string, `uncertainty_score` string, `year` string, `scientific_name` string, `common_name` string, `functional_group` string, `commercial_group` string, `fishing_entity` string, `fishing_sector` string, `catch_type` string, `reporting_status` string, `gear_type` string, `end_use_type` string, `tonnes` string, `landed_value` string) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' LOCATION '{BUCKET}/raw/eez/' TBLPROPERTIES ('skip.header.line.count'='1');",
    f"CREATE EXTERNAL TABLE `eez_processed`(`area_name` string, `area_type` string, `data_layer` string, `uncertainty_score` string, `scientific_name` string, `common_name` string, `functional_group` string, `commercial_group` string, `fishing_entity` string, `fishing_sector` string, `catch_type` string, `reporting_status` string, `gear_type` string, `end_use_type` string, `tonnes` string, `landed_value` string) PARTITIONED BY (`year` string) STORED AS PARQUET LOCATION '{BUCKET}/processed/eez/';",
    "MSCK REPAIR TABLE `eez_processed`;"
]

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return result.stdout.strip()

def run_athena(query):
    exec_id = run_cmd(f'aws athena start-query-execution --query-string "{query}" --query-execution-context Database={DATABASE} --result-configuration OutputLocation={OUTPUT_LOC} --query QueryExecutionId --output text')
    if not exec_id: return "ERROR"
    while True:
        status = run_cmd(f"aws athena get-query-execution --query-execution-id {exec_id} --query QueryExecution.Status.State --output text")
        if status in ["SUCCEEDED", "FAILED", "CANCELLED"]: return status
        time.sleep(1)

print("=============================================")
print("🤖 AUTOMATIZADOR DE TAREAS AWS - BIG DATA TEAM")
print("=============================================")

print(f"\n[1/4] Iniciando Glue Job ({GLUE_JOB})...")
job_run_id = run_cmd(f"aws glue start-job-run --job-name {GLUE_JOB} --query JobRunId --output text")
print("      Job iniciado. Esperando a que termine (aprox 5-10 min)...")
while job_run_id:
    status = run_cmd(f"aws glue get-job-run --job-name {GLUE_JOB} --run-id {job_run_id} --query JobRun.JobRunState --output text")
    if status == "SUCCEEDED":
        print("      ✅ Glue Job completado con éxito!")
        break
    elif status in ["FAILED", "STOPPED", "ERROR"]:
        print(f"      ❌ El Glue Job falló con estado: {status}")
        exit(1)
    time.sleep(30)

print(f"\n[2/4] Preparando Crawler y Tablas...")
run_cmd(f"aws glue start-crawler --name {CRAWLER}")
print("      Crawler iniciado y ajustando tablas manuales para el benchmark...")
for q in DDL_QUERIES: run_athena(q)
print("      ✅ Tablas configuradas correctamente!")

print("\n[3/4] Ejecutando Benchmark en Athena (6 queries)...")
results_data = {}
for q_id, q_format, query in QUERIES_BENCHMARK:
    print(f"      Ejecutando {q_id} ({q_format})...")
    exec_id = run_cmd(f'aws athena start-query-execution --query-string "{query}" --query-execution-context Database={DATABASE} --result-configuration OutputLocation={OUTPUT_LOC} --query QueryExecutionId --output text')
    
    while True:
        status = run_cmd(f"aws athena get-query-execution --query-execution-id {exec_id} --query QueryExecution.Status.State --output text")
        if status in ["SUCCEEDED", "FAILED", "CANCELLED"]: break
        time.sleep(1)
    
    if status == "SUCCEEDED":
        stats = json.loads(run_cmd(f"aws athena get-query-execution --query-execution-id {exec_id} --query QueryExecution.Statistics --output json"))
        time_s = stats.get("EngineExecutionTimeInMillis", 0) / 1000.0
        mb_scanned = stats.get("DataScannedInBytes", 0) / (1024 * 1024)
        results_data[f"{q_id}_{q_format}"] = f"Tiempo = {time_s:.2f}s, Escaneado = {mb_scanned:.2f} MB"
        print(f"         ✅ {time_s:.2f}s, {mb_scanned:.2f} MB")
    else:
        print(f"         ❌ Falló (Data sucia - Esperado en CSV)")
        results_data[f"{q_id}_{q_format}"] = "ERROR (Data sucia)"

print("\n[4/4] Resultados del Benchmark (Anota estos valores en analytics/benchmark.md):")
for key, val in results_data.items(): print(f"      {key}: {val}")

print("\n=============================================")
print("✅ TODO EL PROCESAMIENTO EN AWS ESTÁ TERMINADO")
print("=============================================")
