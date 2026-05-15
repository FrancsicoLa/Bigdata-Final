-- =============================================================================
-- Vista 5: Análisis de captura por zona EEZ y década
-- Pregunta de negocio: ¿Qué zonas económicas exclusivas han tenido mayor
-- actividad pesquera? ¿En qué décadas se concentró la explotación?
-- =============================================================================

CREATE OR REPLACE VIEW analytics_eez_by_decade AS
SELECT 
    area_name AS zona_eez,
    CONCAT(CAST(FLOOR(CAST(year AS INTEGER) / 10) * 10 AS VARCHAR), 's') AS decada,
    ROUND(SUM(CAST(tonnes AS DOUBLE)), 2) AS total_tonnes,
    ROUND(SUM(CAST(landed_value AS DOUBLE)), 2) AS total_valor_usd,
    COUNT(DISTINCT scientific_name) AS num_especies,
    COUNT(DISTINCT fishing_entity) AS num_paises
FROM eez_processed
GROUP BY area_name, FLOOR(CAST(year AS INTEGER) / 10) * 10
HAVING SUM(CAST(tonnes AS DOUBLE)) > 1000
ORDER BY total_tonnes DESC
LIMIT 50;
