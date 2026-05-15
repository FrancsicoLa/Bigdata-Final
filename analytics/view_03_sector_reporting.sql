-- =============================================================================
-- Vista 3: Comparación de captura por sector pesquero y tipo de reporte
-- Pregunta de negocio: ¿Cuánta pesca es industrial vs artesanal? ¿Qué 
-- proporción es reportada oficialmente vs estimada (no reportada)?
-- =============================================================================

CREATE OR REPLACE VIEW analytics_sector_vs_reporting AS
SELECT 
    fishing_sector AS sector,
    reporting_status AS estado_reporte,
    catch_type AS tipo_captura,
    COUNT(*) AS num_registros,
    ROUND(SUM(CAST(tonnes AS DOUBLE)), 2) AS total_tonnes,
    ROUND(SUM(CAST(tonnes AS DOUBLE)) * 100.0 / 
        SUM(SUM(CAST(tonnes AS DOUBLE))) OVER (), 2) AS porcentaje_del_total
FROM eez_processed
GROUP BY fishing_sector, reporting_status, catch_type
ORDER BY total_tonnes DESC;
