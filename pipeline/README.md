# Pipeline - Documentación Técnica (Rol 1: Data Engineer)

## Descripción General
Este módulo es responsable de la **ingesta y transformación** de los datos crudos del proyecto Sea Around Us. Toma 4 archivos CSV desde sus fuentes originales, los carga en la zona `raw/` del Data Lake en Amazon S3, y los transforma a formato Apache Parquet particionado por año en la zona `processed/`.

## Flujo del Pipeline

```
Archivos CSV locales
       │
       ▼
┌─────────────────┐
│  Terraform       │  ← Sube los 4 CSV a S3 (zona raw/)
│  (main.tf)       │  ← Crea el Bucket, Glue Job, Crawler
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AWS Glue Job    │  ← Lee CSV de raw/
│  (glue_job.py)   │  ← Limpia datos (dropna en year)
│                  │  ← Convierte a Parquet
│                  │  ← Particiona por columna "year"
│                  │  ← Escribe en processed/
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AWS Glue        │  ← Lee los Parquet de processed/
│  Crawler         │  ← Detecta esquemas automáticamente
│                  │  ← Crea tablas en Glue Data Catalog
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Glue Data       │  ← Tablas listas para Athena
│  Catalog         │  ← Base de datos: fisheries_db_diego
└─────────────────┘
```

## Archivos del Módulo

| Archivo | Propósito |
| :--- | :--- |
| `scripts/glue_job.py` | Script PySpark que se ejecuta como AWS Glue Job. Lee los 4 CSV de la zona raw, elimina registros sin año y los guarda como Parquet particionado por `year` en la zona processed. |
| `terraform/main.tf` | Infraestructura como código. Define: el Bucket S3, las 3 zonas (raw/processed/curated), la carga de los 4 CSV, el Glue Job, la base de datos del catálogo y el Crawler. |
| `terraform/variables.tf` | Variables de configuración: nombre del bucket y región de AWS. |

## Decisiones de Diseño

### ¿Por qué Terraform y no la consola web?
Terraform permite **reproducir** toda la infraestructura con un solo comando (`terraform apply`). Si el Bucket se borra accidentalmente o si otro equipo quiere replicar el proyecto, solo necesita correr el mismo comando. Esto cumple con el requisito de "pipeline reproducible".

### ¿Por qué Parquet?
- **Formato columnar:** Athena solo lee las columnas que necesita la query, no toda la fila.
- **Compresión nativa:** Reduce el volumen de datos en disco hasta un 80%.
- **Compatible con Glue y Athena** sin configuración extra.

### ¿Por qué particionar por `year`?
- Es la columna de filtro más común en análisis de pesca ("¿cuánto se pescó en 2010?").
- Permite a Athena usar **partition pruning**: si filtras por `WHERE year = 2010`, Athena solo abre la carpeta `year=2010/` e ignora las demás, reduciendo costos hasta un 99%.

### Resolución de esquemas entre fuentes
Los 4 archivos tienen esquemas diferentes:
- `global.csv`: 9 columnas (no tiene `area_name`, `scientific_name`, etc.)
- `eez.csv`: 17 columnas (la más completa)
- `high_seas.csv`: 15 columnas
- `fishing_entity.csv`: 14 columnas (no tiene `fishing_entity` como columna, usa el nombre del archivo como contexto)

En lugar de forzar un esquema único, se decidió **mantener cada fuente como tabla independiente** en el catálogo y resolver la integración en la capa analítica (Athena views).

## Cómo Reproducir

```bash
# 1. Asegurarse de tener los CSV en data_full/
# 2. Configurar AWS CLI con credenciales válidas
# 3. Ejecutar:
cd pipeline/terraform
terraform init
terraform apply
```
