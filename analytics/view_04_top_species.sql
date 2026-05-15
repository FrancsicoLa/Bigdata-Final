-- =============================================================================
-- Vista 4: Top 15 especies más capturadas en alta mar (High Seas)
-- Pregunta de negocio: ¿Cuáles son las especies más explotadas en aguas
-- internacionales? ¿Hay sobreexplotación de especies comerciales clave?
-- =============================================================================

CREATE OR REPLACE VIEW analytics_top_species_high_seas AS
SELECT 
    common_name AS especie_comun,
    scientific_name AS nombre_cientifico,
    commercial_group AS grupo_comercial,
    functional_group AS grupo_funcional,
    ROUND(SUM(CAST(tonnes AS DOUBLE)), 2) AS total_tonnes,
    COUNT(DISTINCT fishing_entity) AS num_paises_que_pescan,
    COUNT(DISTINCT year) AS anios_con_actividad
FROM high_seas_processed
WHERE common_name IS NOT NULL 
  AND common_name != 'Marine fishes nei'
GROUP BY common_name, scientific_name, commercial_group, functional_group
ORDER BY total_tonnes DESC
LIMIT 15;
