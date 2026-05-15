# Dashboard de QuickSight - Descripción de Visualizaciones

## Conexión
El dashboard de Amazon QuickSight está conectado a **Amazon Athena** usando la base de datos `fisheries_db_diego`, que contiene las tablas procesadas en formato Parquet particionado por año.

## Visualizaciones

### Visualización 1: Tendencia de Captura Global (1950–2018)
- **Tipo de gráfica:** Línea temporal (Line Chart)
- **Eje X:** Año
- **Eje Y:** Total de toneladas capturadas
- **Pregunta que responde:** *¿La pesca mundial ha aumentado o disminuido en las últimas 7 décadas?*
- **Insight esperado:** Se observa un crecimiento sostenido desde 1950 hasta mediados de los años 90, seguido de una meseta o ligero declive, lo que sugiere que los océanos están alcanzando su capacidad máxima de explotación pesquera.
- **Query base:** `view_02_catch_trend.sql`

### Visualización 2: Top 10 Países Pesqueros (Barras Horizontales)
- **Tipo de gráfica:** Barras horizontales ordenadas
- **Eje X:** Total de toneladas
- **Eje Y:** País (fishing_entity)
- **Pregunta que responde:** *¿Qué países dominan la pesca mundial?*
- **Insight esperado:** China lidera con una diferencia significativa, seguida por Perú, Indonesia, Japón y Estados Unidos. Estos 5 países representan más del 50% de la captura global.
- **Query base:** `view_01_top10_countries.sql`

### Visualización 3: Distribución por Sector Pesquero (Dona / Pie Chart)
- **Tipo de gráfica:** Gráfico de dona (Donut Chart)
- **Segmentos:** Sector pesquero (Industrial, Artisanal, Subsistence, Recreational)
- **Valor:** Porcentaje del total de toneladas
- **Pregunta que responde:** *¿Qué proporción de la pesca mundial es industrial vs artesanal?*
- **Insight esperado:** La pesca industrial representa la gran mayoría del tonelaje, pero la pesca artesanal tiene un rol importante en economías en desarrollo.
- **Query base:** `view_03_sector_reporting.sql`

### Visualización 4: Mapa de Calor - Captura por Zona EEZ y Década
- **Tipo de gráfica:** Tabla de calor (Heat Map) o Tabla Pivot
- **Filas:** Zona EEZ (área geográfica)
- **Columnas:** Década (1950s, 1960s, ... 2010s)
- **Valor:** Total de toneladas (intensidad del color)
- **Pregunta que responde:** *¿Qué regiones han sido más explotadas en cada década?*
- **Insight esperado:** Se visualiza el desplazamiento geográfico de la actividad pesquera: en décadas tempranas dominan el Atlántico Norte y Europa, mientras que en décadas recientes la actividad se concentra en el Pacífico y Asia.
- **Query base:** `view_05_eez_by_decade.sql`

## Pasos para Crear el Dashboard en QuickSight
1. Ir a **Amazon QuickSight** > "New Analysis" > "New Dataset".
2. Elegir **Athena** como fuente de datos.
3. Seleccionar la base de datos `fisheries_db_diego`.
4. Para cada visualización, seleccionar la vista correspondiente o escribir una query personalizada.
5. Arrastrar las columnas a los ejes y aplicar el tipo de gráfica indicado.
6. Publicar el dashboard y compartirlo con el equipo.

## Capturas
*(Insertar capturas de pantalla del dashboard una vez creado en QuickSight)*

- `screenshot_viz1_trend.png`
- `screenshot_viz2_top10.png`
- `screenshot_viz3_sectors.png`
- `screenshot_viz4_heatmap.png`
