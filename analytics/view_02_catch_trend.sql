-- =============================================================================
-- Vista 2: Tendencia de captura global por año
-- Pregunta de negocio: ¿Cómo ha evolucionado la captura pesquera mundial
-- a lo largo de las décadas? ¿Está aumentando o disminuyendo?
-- =============================================================================

CREATE OR REPLACE VIEW analytics_catch_trend_by_year AS
SELECT 
    CAST(year AS INTEGER) AS anio,
    ROUND(SUM(CAST(tonnes AS DOUBLE)), 2) AS total_tonnes,
    ROUND(SUM(CAST(landed_value AS DOUBLE)), 2) AS total_valor_usd,
    COUNT(DISTINCT fishing_entity) AS num_paises_activos,
    ROUND(AVG(CAST(tonnes AS DOUBLE)), 4) AS promedio_tonnes_por_registro
FROM global_processed
GROUP BY year
ORDER BY anio;
