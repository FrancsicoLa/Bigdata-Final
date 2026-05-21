import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

bucket = "big-data-project-gang-582465846893"

# Leer CSV
df_global = spark.read.option("header", True).csv(f"s3://{bucket}/raw/global/")
df_eez = spark.read.option("header", True).csv(f"s3://{bucket}/raw/eez/")
df_high = spark.read.option("header", True).csv(f"s3://{bucket}/raw/high_seas/")
df_entity = spark.read.option("header", True).csv(f"s3://{bucket}/raw/fishing_entity/")

# Transformar (ejemplo mínimo)
df_global = df_global.dropna(subset=["year"])

# Guardar en Parquet + partición
df_global.write.partitionBy("year").mode("overwrite").parquet(f"s3://{bucket}/processed/global/")
df_eez.write.partitionBy("year").mode("overwrite").parquet(f"s3://{bucket}/processed/eez/")
df_high.write.partitionBy("year").mode("overwrite").parquet(f"s3://{bucket}/processed/high_seas/")
df_entity.write.partitionBy("year").mode("overwrite").parquet(f"s3://{bucket}/processed/fishing_entity/")