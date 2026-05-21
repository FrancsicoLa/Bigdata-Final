provider "aws" {
  region = var.region
}

data "aws_caller_identity" "current" {}

# -------------------------
# CREACION DEL BUCKET S3
# -------------------------
resource "aws_s3_bucket" "data_lake" {
  bucket        = "${var.bucket_name}-${data.aws_caller_identity.current.account_id}"
  force_destroy = true
}

# -------------------------
# ESTRUCTURA DEL DATA LAKE
# -------------------------
resource "aws_s3_object" "raw" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "raw/"
}

resource "aws_s3_object" "processed" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "processed/"
}

resource "aws_s3_object" "curated" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "curated/"
}

# -------------------------
# SUBIR CSV (RAW ZONE)
# -------------------------
resource "aws_s3_object" "global_csv" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "raw/global/global.csv"
  source = "../../data_full/global.csv"
}

resource "aws_s3_object" "eez_csv" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "raw/eez/eez.csv"
  source = "../../data_full/eez.csv"
}

resource "aws_s3_object" "high_csv" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "raw/high_seas/high_seas.csv"
  source = "../../data_full/high_seas.csv"
}

resource "aws_s3_object" "entity_csv" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "raw/fishing_entity/fishing_entity.csv"
  source = "../../data_full/fishing_entity.csv"
}

# -------------------------
# USAR DATABASE EXISTENTE (FIX ERROR)
# -------------------------
resource "aws_glue_catalog_database" "db" {
  name = "fisheries_db_diego"
}

# -------------------------
# SUBIR SCRIPT DE GLUE
# -------------------------
resource "aws_s3_object" "glue_script" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "scripts/glue_job.py"
  source = "../scripts/glue_job.py"
}

# -------------------------
# GLUE JOB
# -------------------------
resource "aws_glue_job" "transform_job" {
  name     = "transform-fisheries"
  role_arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/GlueCrawlerRole"

  command {
    script_location = "s3://${aws_s3_bucket.data_lake.bucket}/scripts/glue_job.py"
    python_version  = "3"
  }

  glue_version = "4.0"
}

# -------------------------
# GLUE CRAWLER
# -------------------------
resource "aws_glue_crawler" "crawler" {
  name          = "fisheries-crawler_gang"
  role          = "GlueCrawlerRole"
  database_name = aws_glue_catalog_database.db.name

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.bucket}/processed/"
  }

  depends_on = [aws_glue_job.transform_job]
}