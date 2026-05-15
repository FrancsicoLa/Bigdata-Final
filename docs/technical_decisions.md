# Decisiones Técnicas (ADRs)

Este documento registra las decisiones técnicas clave tomadas por el equipo a lo largo del proyecto. No se trata de un manual de usuario, sino de justificar el **"por qué"** detrás de cada elección técnica.

## 1. Uso de formato Parquet
- **Contexto:** Los datos originales del proyecto "Sea Around Us" vienen en formato CSV (texto plano).
- **Decisión:** Se definió transformar todos los datos crudos a formato Apache Parquet dentro del Data Lake en S3.
- **Justificación:** Parquet es un formato de almacenamiento columnar. Athena solo lee las columnas que necesita la query (no toda la fila), lo que reduce drásticamente el volumen de datos escaneados, acelerando las consultas y minimizando los costos. En nuestro benchmark, el ahorro fue de hasta **99.5% en bytes escaneados**.

## 2. Particionamiento por columna `year`
- **Contexto:** Se necesita organizar los archivos Parquet en S3 para lectura óptima.
- **Decisión:** Se particionó la tabla principal utilizando la columna `year`.
- **Justificación:** El año es la dimensión de filtro más frecuente en análisis pesquero ("¿cuánto se pescó en 2010?"). Al crear carpetas `year=1950/`, `year=1951/`, etc., Athena aplica **partition pruning**: solo abre la carpeta que coincide con el filtro `WHERE` e ignora las demás. Esto convierte una consulta de 61 MB a solo 0.3 MB.

## 3. Herramienta de Orquestación: AWS Step Functions + Bash Script
- **Contexto:** Se requiere ejecutar el pipeline de extremo a extremo sin intervención manual.
- **Decisión:** Se implementaron dos opciones: AWS Step Functions (preferida) y un script bash como alternativa.
- **Justificación:** Step Functions ofrece manejo de errores nativo, reintentos automáticos y un diagrama visual del flujo. El bash script se incluyó como respaldo para entornos donde Step Functions no esté disponible o para debugging rápido.

## 4. Framework de Calidad de Datos: Pandas con aserciones nativas
- **Contexto:** Es necesario automatizar y estandarizar la evaluación de reglas de calidad.
- **Decisión:** Se usó Python con Pandas y validaciones programáticas (sin frameworks externos como Great Expectations).
- **Justificación:** Pandas es la herramienta más accesible para el equipo y no requiere instalación de paquetes adicionales más allá de la librería estándar de análisis de datos. Las 10 reglas se implementaron como funciones reutilizables que generan un reporte HTML profesional.

## 5. Infraestructura como Código: Terraform
- **Contexto:** Se necesita crear y configurar múltiples recursos de AWS (S3, Glue, Crawler).
- **Decisión:** Se utilizó Terraform en lugar de crear los recursos manualmente desde la consola web.
- **Justificación:** Terraform permite reproducir toda la infraestructura con un solo comando (`terraform apply`). Si otro equipo o el profesor quieren replicar el proyecto, solo necesitan las credenciales de AWS y ejecutar el comando. Esto cumple con el requisito de "pipeline reproducible".

## 6. Tablas independientes por fuente (sin schema unificado)
- **Contexto:** Los 4 archivos CSV tienen esquemas diferentes (entre 9 y 17 columnas).
- **Decisión:** Se mantuvo cada fuente como tabla independiente en el catálogo de Glue en lugar de forzar un esquema único.
- **Justificación:** Forzar un esquema único requeriría renombrar o eliminar columnas, perdiendo información valiosa. La integración se resuelve en la capa analítica (vistas de Athena), lo que sigue el principio de **schema-on-read** que pide la rúbrica.

## 7. Elección del 4to archivo: `fishing_entity.csv`
- **Contexto:** La Ruta A exige agregar al menos un 4to archivo adicional de Sea Around Us.
- **Decisión:** Se eligió el archivo de "Fishing Entity" que contiene datos de captura desglosados por país.
- **Justificación:** Este archivo aporta ~791K filas adicionales y permite hacer análisis cruzados de integridad referencial (DQ-10) entre las entidades pesqueras de los distintos datasets, enriqueciendo tanto la capa de calidad como la analítica.
