-- =============================================================================
-- BENCHMARK QUERIES
-- Estas 3 consultas deben ejecutarse en Amazon Athena dos veces cada una:
--   1) Contra la tabla RAW (CSV sin partición)
--   2) Contra la tabla PROCESSED (Parquet particionado por year)
-- Anotar el tiempo de ejecución y bytes escaneados de cada ejecución.
-- =============================================================================

-- -------------------------------------------------------
-- Q1: Total de captura por año (Agregación simple)
-- -------------------------------------------------------
-- Version CSV (raw):
SELECT year, SUM(CAST(tonnes AS DOUBLE)) AS total_tonnes
FROM global_raw
GROUP BY year
ORDER BY year;

-- Version Parquet (processed):
SELECT year, SUM(CAST(tonnes AS DOUBLE)) AS total_tonnes
FROM global_processed
GROUP BY year
ORDER BY year;

-- -------------------------------------------------------
-- Q2: Top 5 países por captura en un año específico (Filtro + Agregación)
-- -------------------------------------------------------
-- Version CSV (raw):
SELECT fishing_entity, SUM(CAST(tonnes AS DOUBLE)) AS total_tonnes
FROM global_raw
WHERE year = '2010'
GROUP BY fishing_entity
ORDER BY total_tonnes DESC
LIMIT 5;

-- Version Parquet (processed):
SELECT fishing_entity, SUM(CAST(tonnes AS DOUBLE)) AS total_tonnes
FROM global_processed
WHERE year = '2010'
GROUP BY fishing_entity
ORDER BY total_tonnes DESC
LIMIT 5;

-- -------------------------------------------------------
-- Q3: Captura por sector y tipo en EEZ (JOIN implícito + múltiples agrupaciones)
-- -------------------------------------------------------
-- Version CSV (raw):
SELECT fishing_sector, catch_type, reporting_status,
       COUNT(*) AS registros,
       SUM(CAST(tonnes AS DOUBLE)) AS total_tonnes
FROM eez_raw
WHERE CAST(year AS INTEGER) BETWEEN 2000 AND 2018
GROUP BY fishing_sector, catch_type, reporting_status
ORDER BY total_tonnes DESC;

-- Version Parquet (processed):
SELECT fishing_sector, catch_type, reporting_status,
       COUNT(*) AS registros,
       SUM(CAST(tonnes AS DOUBLE)) AS total_tonnes
FROM eez_processed
WHERE CAST(year AS INTEGER) BETWEEN 2000 AND 2018
GROUP BY fishing_sector, catch_type, reporting_status
ORDER BY total_tonnes DESC;
