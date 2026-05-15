-- =============================================================================
-- Vista 1: Top 10 países con mayor captura total histórica
-- Pregunta de negocio: ¿Cuáles son los países que más han pescado en la 
-- historia y cuánto representan en toneladas y valor económico?
-- =============================================================================

CREATE OR REPLACE VIEW analytics_top10_fishing_countries AS
SELECT 
    fishing_entity AS pais,
    ROUND(SUM(CAST(tonnes AS DOUBLE)), 2) AS total_tonnes,
    ROUND(SUM(CAST(landed_value AS DOUBLE)), 2) AS total_valor_usd,
    COUNT(*) AS total_registros
FROM global_processed
GROUP BY fishing_entity
ORDER BY total_tonnes DESC
LIMIT 10;
