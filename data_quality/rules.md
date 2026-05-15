# Reglas de Calidad de Datos

Este documento define las 8+ reglas de validación que el equipo aplicará sobre los datasets de Sea Around Us para asegurar la integridad, completitud y consistencia de los datos antes de su uso analítico.

## Resumen de Reglas

| ID | Nombre | Tipo | Severidad | Columnas Afectadas |
| :--- | :--- | :--- | :--- | :--- |
| DQ-01 | Completitud de campos críticos | Completitud | 🔴 Alta | `year`, `tonnes`, `fishing_entity` |
| DQ-02 | Validez temporal | Rango | 🔴 Alta | `year` |
| DQ-03 | No negatividad de tonelaje | Rango | 🔴 Alta | `tonnes` |
| DQ-04 | No negatividad de valor económico | Rango | 🟡 Media | `landed_value` |
| DQ-05 | Valores válidos de sector pesquero | Dominio | 🟡 Media | `fishing_sector` |
| DQ-06 | Valores válidos de tipo de captura | Dominio | 🟡 Media | `catch_type` |
| DQ-07 | Valores válidos de estado de reporte | Dominio | 🟡 Media | `reporting_status` |
| DQ-08 | Consistencia entre tipo de captura y uso final | Consistencia | 🟢 Baja | `catch_type`, `end_use_type` |
| DQ-09 | Unicidad de registros | Unicidad | 🟡 Media | Todas las columnas clave |
| DQ-10 | Integridad referencial entre fuentes | Integridad Referencial | 🔴 Alta | `fishing_entity` |

---

## Detalle de Cada Regla

### DQ-01: Completitud de campos críticos
- **Tipo:** Completitud (Nulls / NaN)
- **Severidad:** 🔴 Alta
- **Justificación de negocio:** Los campos `year`, `tonnes` y `fishing_entity` son las dimensiones mínimas necesarias para cualquier análisis de pesca. Sin año no podemos ubicar el dato en el tiempo; sin tonelaje no hay métrica; sin entidad pesquera no hay sujeto de análisis. Un registro sin estos campos es inutilizable.
- **Regla:** Ninguno de los campos `year`, `tonnes`, `fishing_entity` puede ser nulo o vacío en ningún dataset.

### DQ-02: Validez temporal
- **Tipo:** Rango válido
- **Severidad:** 🔴 Alta
- **Justificación de negocio:** Según la documentación oficial de Sea Around Us, los datos cubren el período 1950–2018. Cualquier año fuera de este rango indica corrupción de datos, errores de carga o mezcla con fuentes externas no autorizadas.
- **Regla:** `year` debe estar entre 1950 y 2018 (inclusive) en todos los datasets.

### DQ-03: No negatividad de tonelaje
- **Tipo:** Rango válido
- **Severidad:** 🔴 Alta
- **Justificación de negocio:** Las toneladas de captura representan una cantidad física. Un valor negativo no tiene sentido en el mundo real y podría distorsionar totales, promedios y gráficas del dashboard, generando conclusiones erróneas.
- **Regla:** `tonnes` debe ser ≥ 0 en todos los registros.

### DQ-04: No negatividad de valor económico
- **Tipo:** Rango válido
- **Severidad:** 🟡 Media
- **Justificación de negocio:** El campo `landed_value` representa el valor comercial de la captura en dólares. Un valor negativo indicaría una transacción imposible. Se permite nulo (ya que algunos registros no tienen valuación), pero si tiene valor, debe ser positivo.
- **Regla:** Donde `landed_value` no sea nulo, debe ser ≥ 0.

### DQ-05: Valores válidos de sector pesquero
- **Tipo:** Dominio (lista cerrada)
- **Severidad:** 🟡 Media
- **Justificación de negocio:** Sea Around Us clasifica la pesca en sectores conocidos. Un valor fuera de la lista indicaría un error de transcripción o una categoría no reconocida que invalidaría los análisis por sector.
- **Regla:** `fishing_sector` solo puede contener: `Industrial`, `Artisanal`, `Subsistence`, `Recreational`.

### DQ-06: Valores válidos de tipo de captura
- **Tipo:** Dominio (lista cerrada)
- **Severidad:** 🟡 Media
- **Justificación de negocio:** El tipo de captura (desembarques vs. descartes) es una dimensión analítica clave para entender cuánto del recurso pesquero realmente llega al mercado.
- **Regla:** `catch_type` solo puede contener: `Landings`, `Discards`.

### DQ-07: Valores válidos de estado de reporte
- **Tipo:** Dominio (lista cerrada)
- **Severidad:** 🟡 Media
- **Justificación de negocio:** Distinguir entre datos reportados oficialmente y estimaciones no reportadas es fundamental para medir la confiabilidad de las cifras del dashboard.
- **Regla:** `reporting_status` solo puede contener: `Reported`, `Unreported`.

### DQ-08: Consistencia entre tipo de captura y uso final
- **Tipo:** Consistencia entre columnas
- **Severidad:** 🟢 Baja
- **Justificación de negocio:** Si un registro indica que la captura fue de tipo `Discards` (descarte/basura), no debería tener un `end_use_type` de `Direct human consumption` (consumo humano directo), ya que eso es una contradicción lógica que sugiere un error de clasificación.
- **Regla:** Si `catch_type` == `Discards`, entonces `end_use_type` NO debe ser `Direct human consumption`.

### DQ-09: Unicidad de registros
- **Tipo:** Unicidad (duplicados)
- **Severidad:** 🟡 Media
- **Justificación de negocio:** Registros duplicados inflan artificialmente las estadísticas de captura, lo que llevaría a conclusiones erróneas sobre la producción pesquera de un país o región.
- **Regla:** No deben existir filas completamente duplicadas dentro de cada dataset individual.

### DQ-10: Integridad referencial entre fuentes
- **Tipo:** Integridad referencial
- **Severidad:** 🔴 Alta
- **Justificación de negocio:** Al integrar múltiples fuentes (Global, EEZ, High Seas, Fishing Entity), es crítico que las entidades pesqueras (países) sean consistentes. Si un país aparece en el dataset EEZ pero no existe en el dataset Global, los JOINs analíticos producirían datos huérfanos.
- **Regla:** Al menos el 80% de los valores únicos de `fishing_entity` en los datasets EEZ y High Seas deben existir también en el dataset Global.
