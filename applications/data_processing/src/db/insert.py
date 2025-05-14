import logging

import boto3
import click
from client import DBClient
from pyspark.sql import DataFrame, SparkSession


def write_jdbc(dataframe: DataFrame, name: str, jdbc_url: str, connection_properties: dict):
    dataframe.write.jdbc(
        url=jdbc_url,
        table=f"public.{name}",
        mode="append",
        properties=connection_properties,
    )


@click.command()
@click.option("--profile", help="AWS profile name")
@click.option("--region", help="Database name")
@click.option("--s3-dir", help="Location of normalized parquet files on S3")
def main(profile: str, region: str, s3_dir: str):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    session = boto3.Session(region_name=region, profile_name=profile)
    credentials = session.get_credentials().get_frozen_credentials()
    logger.info(f"Using AWS profile {profile} in {region}")

    ssm = session.client("ssm")
    db_client = DBClient.from_ssm("db", ssm)
    logger.info(f"Created PostgreSQL client for {db_client.host}")

    spark = (
        SparkSession.builder.appName("S3ToSql")
        .config(
            "spark.jars.packages",
            "org.apache.hadoop:hadoop-aws:3.3.2,com.amazonaws:aws-java-sdk-bundle:1.11.1026",
        )
        .config("spark.jars", "postgresql-42.5.0.jar")
        .getOrCreate()
    )

    hadoop_conf = spark.sparkContext._jsc.hadoopConfiguration()

    # Set AWS credentials for s3a
    hadoop_conf.set(
        "fs.s3a.aws.credentials.provider",
        "org.apache.hadoop.fs.s3a.TemporaryAWSCredentialsProvider",
    )
    hadoop_conf.set("fs.s3a.access.key", credentials.access_key)
    hadoop_conf.set("fs.s3a.secret.key", credentials.secret_key)
    hadoop_conf.set("fs.s3a.session.token", credentials.token)

    logger.info("Loading parquet files from S3")
    countries = spark.read.parquet(f"s3a://{s3_dir}/countries/")
    answers = spark.read.parquet(f"s3a://{s3_dir}/answers/")
    lang = spark.read.parquet(f"s3a://{s3_dir}/lang/")
    db = spark.read.parquet(f"s3a://{s3_dir}/db/")
    lah = spark.read.parquet(f"s3a://{s3_dir}/lah/")
    law = spark.read.parquet(f"s3a://{s3_dir}/law/")
    dah = spark.read.parquet(f"s3a://{s3_dir}/dah/")
    daw = spark.read.parquet(f"s3a://{s3_dir}/daw/")
    logger.info("Loaded normalized data")

    logger.info(f"Writing data to PostgreSQL with {db_client.jdbc_url=}")
    write_jdbc(countries, "countries", db_client.jdbc_url, db_client.jdbc_connection)
    write_jdbc(lang, "lang", db_client.jdbc_url, db_client.jdbc_connection)
    write_jdbc(db, "db", db_client.jdbc_url, db_client.jdbc_connection)
    write_jdbc(lah, "lah", db_client.jdbc_url, db_client.jdbc_connection)
    write_jdbc(law, "law", db_client.jdbc_url, db_client.jdbc_connection)
    write_jdbc(dah, "dah", db_client.jdbc_url, db_client.jdbc_connection)
    write_jdbc(daw, "daw", db_client.jdbc_url, db_client.jdbc_connection)
    write_jdbc(answers, "answers", db_client.jdbc_url, db_client.jdbc_connection)  # write answers last
    logger.info("Finished writing data to PostgreSQL")


if __name__ == "__main__":
    main()
