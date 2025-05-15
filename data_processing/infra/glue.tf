resource "aws_glue_catalog_database" "data_processing_db" {
  name = "survey_db"
}

resource "aws_glue_classifier" "csv_classifier" {
  name = "custom-csv-classifier"
  csv_classifier {
    allow_single_column = false
    contains_header     = "PRESENT"
    delimiter           = ","
    quote_symbol        = "\""
  }
}

resource "aws_glue_crawler" "raw_data_crawler" {
  name          = "raw-data-crawler"
  role          = data.aws_iam_role.main_role.arn
  database_name = aws_glue_catalog_database.data_processing_db.name

  s3_target {
    path = "s3://${aws_s3_bucket.data.bucket}/${var.raw_data_directory}/"
  }

  configuration = jsonencode({
    "Version" = 1.0,
    "CrawlerOutput" = {
      "Partitions" = {
        "AddOrUpdateBehavior" = "InheritFromTable"
      }
    }
  })

  classifiers = [
    aws_glue_classifier.csv_classifier.name
  ]

  recrawl_policy {
    recrawl_behavior = "CRAWL_EVERYTHING"
  }

  schema_change_policy {
    update_behavior = "UPDATE_IN_DATABASE"
    delete_behavior = "DEPRECATE_IN_DATABASE"
  }
}

resource "aws_glue_catalog_table" "raw_glue_table" {
  name          = "raw"
  database_name = aws_glue_catalog_database.data_processing_db.name

  storage_descriptor {
    location = "s3://${aws_s3_bucket.data.bucket}/${var.raw_data_directory}/"

    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"

    ser_de_info {
      name                  = "raw_serde"
      serialization_library = "org.apache.hadoop.hive.serde2.OpenCSVSerde"
      parameters = {
        "field.delim"   = ","
        "quoteChar"     = "\""
        "escapeChar"    = "\\"
        "separatorChar" = ","
      }
    }
  }

  table_type = "EXTERNAL_TABLE"
}

resource "aws_glue_catalog_table" "processed_glue_table" {
  name          = "processed"
  database_name = aws_glue_catalog_database.data_processing_db.name

  storage_descriptor {
    location = "s3://${aws_s3_bucket.data.bucket}/${var.processed_data_directory}/"

    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      name                  = "dps_processed_data_serde"
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "years_code"
      type = "int"
    }
    columns {
      name = "years_code_pro"
      type = "int"
    }
    columns {
      name = "country"
      type = "string"
    }
    columns {
      name = "ed_level"
      type = "string"
    }
    columns {
      name = "language_have_worked_with"
      type = "array<string>"
    }
    columns {
      name = "database_have_worked_with"
      type = "array<string>"
    }
    columns {
      name = "language_want_to_work_with"
      type = "array<string>"
    }
    columns {
      name = "database_want_to_work_with"
      type = "array<string>"
    }
  }

  table_type = "EXTERNAL_TABLE"
}


module "glue_ingest_job" {
  source = "./modules/glue_etl"

  name     = "dps-ingest"
  env      = "dev"
  role_arn = data.aws_iam_role.main_role.arn

  glue_assets_bucket = aws_s3_bucket.glue_assets.bucket
  logs_s3_uri        = "s3://${aws_s3_object.sparklogs.bucket}/${aws_s3_object.sparklogs.key}"
  script_path        = "${path.module}/../src/glue/ingest.py"
  scripts_directory  = var.scripts_directory

  arguments = {
    "--glue_database"          = aws_glue_catalog_database.data_processing_db.name
    "--input_glue_table_name"  = aws_glue_catalog_table.raw_glue_table.name
    "--output_glue_table_name" = aws_glue_catalog_table.processed_glue_table.name
    "--source_label"           = "default"
  }
}

module "glue_transform_job" {
  source = "./modules/glue_etl"

  name     = "dps-transform"
  env      = "dev"
  role_arn = data.aws_iam_role.main_role.arn

  glue_assets_bucket = aws_s3_bucket.glue_assets.bucket
  logs_s3_uri        = "s3://${aws_s3_object.sparklogs.bucket}/${aws_s3_object.sparklogs.key}"
  script_path        = "${path.module}/../src/glue/transform.py"
  scripts_directory  = var.scripts_directory

  arguments = {
    "--glue_database"         = aws_glue_catalog_database.data_processing_db.name
    "--input_glue_table_name" = aws_glue_catalog_table.processed_glue_table.name
    "--output_s3_dir"         = "s3://${aws_s3_bucket.data.bucket}/${var.normalized_data_directory}/"
  }
}
