#!/bin/bash
# =============================================================================
# run_pipeline.sh - Script maestro de orquestación
# Proyecto Final - AWS Academy Data Engineering
# Rol 4: Orchestration & Operations Engineer
# =============================================================================
# Este script ejecuta el pipeline completo de forma secuencial:
#   1. Ejecuta el Glue Job (CSV -> Parquet)
#   2. Espera a que termine
#   3. Ejecuta el Crawler (catalogar tablas)
#   4. Espera a que termine
#   5. Ejecuta una query de validación en Athena
#
# Uso:
#   chmod +x run_pipeline.sh
#   ./run_pipeline.sh
#
# Requisitos:
#   - AWS CLI configurado con credenciales válidas
#   - Permisos: Glue, Athena, S3
# =============================================================================

set -e  # Detener ejecución si algún comando falla

GLUE_JOB_NAME="transform-fisheries"
CRAWLER_NAME="fisheries-crawler_gang"
ATHENA_DB="fisheries_db_diego"
ATHENA_OUTPUT="s3://big-data-project-gang-489909410108/athena-results/"

echo "=============================================="
echo "  PIPELINE DE DATA ENGINEERING - Sea Around Us"
echo "=============================================="
echo ""

# -------------------------------------------------
# PASO 1: Ejecutar el Glue Job
# -------------------------------------------------
echo "[1/5] Iniciando Glue Job: $GLUE_JOB_NAME ..."
JOB_RUN_ID=$(aws glue start-job-run --job-name "$GLUE_JOB_NAME" --query 'JobRunId' --output text)

if [ -z "$JOB_RUN_ID" ]; then
    echo "  ERROR: No se pudo iniciar el Glue Job."
    exit 1
fi
echo "  Job Run ID: $JOB_RUN_ID"

# -------------------------------------------------
# PASO 2: Esperar a que termine el Glue Job
# -------------------------------------------------
echo "[2/5] Esperando a que el Glue Job termine..."
while true; do
    STATUS=$(aws glue get-job-run --job-name "$GLUE_JOB_NAME" --run-id "$JOB_RUN_ID" --query 'JobRun.JobRunState' --output text)
    echo "  Estado actual: $STATUS"
    
    if [ "$STATUS" = "SUCCEEDED" ]; then
        echo "  Glue Job completado exitosamente."
        break
    elif [ "$STATUS" = "FAILED" ] || [ "$STATUS" = "STOPPED" ] || [ "$STATUS" = "ERROR" ]; then
        echo "  ERROR: El Glue Job terminó con estado: $STATUS"
        echo "  Revisa los logs en CloudWatch para más detalles."
        exit 1
    fi
    
    sleep 30  # Revisar cada 30 segundos
done

# -------------------------------------------------
# PASO 3: Ejecutar el Crawler
# -------------------------------------------------
echo "[3/5] Iniciando Crawler: $CRAWLER_NAME ..."
aws glue start-crawler --name "$CRAWLER_NAME"
echo "  Crawler iniciado."

# -------------------------------------------------
# PASO 4: Esperar a que termine el Crawler
# -------------------------------------------------
echo "[4/5] Esperando a que el Crawler termine..."
sleep 15  # Espera inicial para que el Crawler arranque

while true; do
    CRAWLER_STATE=$(aws glue get-crawler --name "$CRAWLER_NAME" --query 'Crawler.State' --output text)
    echo "  Estado actual: $CRAWLER_STATE"
    
    if [ "$CRAWLER_STATE" = "READY" ]; then
        echo "  Crawler completado exitosamente."
        break
    fi
    
    sleep 15
done

# -------------------------------------------------
# PASO 5: Validación con Athena
# -------------------------------------------------
echo "[5/5] Ejecutando query de validación en Athena..."
QUERY_ID=$(aws athena start-query-execution \
    --query-string "SELECT COUNT(*) AS total_rows FROM global_processed" \
    --query-execution-context "Database=$ATHENA_DB" \
    --result-configuration "OutputLocation=$ATHENA_OUTPUT" \
    --query 'QueryExecutionId' --output text)

echo "  Query ID: $QUERY_ID"

# Esperar resultado
sleep 10
QUERY_STATUS=$(aws athena get-query-execution --query-execution-id "$QUERY_ID" --query 'QueryExecution.Status.State' --output text)

if [ "$QUERY_STATUS" = "SUCCEEDED" ]; then
    echo "  Validación exitosa: Los datos están disponibles en Athena."
else
    echo "  ADVERTENCIA: La validación en Athena terminó con estado: $QUERY_STATUS"
fi

echo ""
echo "=============================================="
echo "  PIPELINE COMPLETADO EXITOSAMENTE"
echo "=============================================="
echo "  - Datos transformados a Parquet en S3"
echo "  - Tablas catalogadas en Glue Data Catalog"
echo "  - Datos disponibles para consulta en Athena"
echo "=============================================="
