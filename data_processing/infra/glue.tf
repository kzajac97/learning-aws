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
  table_prefix  = "raw_"

  s3_target {
    path = "s3://${aws_s3_bucket.raw_data.bucket}/"
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
  name          = "raw_dps_ingest_data"
  database_name = aws_glue_catalog_database.data_processing_db.name

  storage_descriptor {
    location = "s3://${aws_s3_bucket.raw_data.bucket}/"

    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"

    ser_de_info {
      name                 = "raw_dps_ingest_data_serde"
      serialization_library = "org.apache.hadoop.hive.serde2.OpenCSVSerde"
      parameters = {
        "field.delim" = ","
        "quoteChar"   = "\""
        "escapeChar"  = "\\"
        "separatorChar" = ","
      }
    }
  }

  table_type = "EXTERNAL_TABLE"
}

resource "aws_glue_catalog_table" "processed_glue_table" {
  name          = "dps_processed_data"
  database_name = aws_glue_catalog_database.data_processing_db.name

  storage_descriptor {
    location = "s3://${aws_s3_bucket.processed_data.bucket}/"

    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      name                 = "dps_processed_data_serde"
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "age"
      type = "int"
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
