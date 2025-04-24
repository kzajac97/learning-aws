import dataclasses
import sys
from typing import Final

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

# glue job parameters
GLUE_INPUTS: Final[list[str]] = [
    "JOB_NAME",
    "glue_database",
    "input_glue_table_name",
]


@dataclasses.dataclass
class Context:
    spark: SparkContext
    glue: GlueContext
    glue_job: Job
    # args
    job_name: str
    database: str
    input_table_name: str

    @classmethod
    def from_argv(cls, argv: dict):
        parameters = getResolvedOptions(argv, GLUE_INPUTS)

        return cls(
            spark=SparkContext.getOrCreate(),
            glue=GlueContext(SparkContext.getOrCreate()),
            glue_job=Job(GlueContext(SparkContext.getOrCreate())),
            job_name=parameters["JOB_NAME"],
            database=parameters["glue_database"],
            input_table_name=parameters["input_glue_table_name"],
        )


def pretransform(dataframe: DataFrame) -> DataFrame:
    return dataframe.na.drop(how="any")


def create_country(dataframe: DataFrame) -> DataFrame:
    countries = (
        dataframe.select(F.col("country").alias("name"))
        .filter(F.col("name").isNotNull())
        .distinct()
        .withColumn("id", F.row_number().over(Window.orderBy("name")))
    )
    countries = countries.select("id", "name")
    return countries


def create_from_union(dataframe: DataFrame, alias: str, left: str, right: str) -> DataFrame:
    left = dataframe.select(F.explode(left).alias(alias))
    right = dataframe.select(F.explode(right).alias(alias))

    union = (
        left.union(right)
        .filter(F.col(alias).isNotNull())
        .distinct()
        .withColumnRenamed(alias, "name")
        .withColumn("id", F.row_number().over(Window.orderBy("name")))
        .select("id", "name")
    )

    return union


def create_answers(dataframe: DataFrame) -> DataFrame:
    answers = dataframe.select(
        F.monotonically_increasing_id().alias("id"),
        "years_code",
        "years_code_pro",
        F.col("ed_level"),
        F.col("country").alias("country_name"),
    )

    return answers


def index_countries(answers: DataFrame, countries: DataFrame) -> DataFrame:
    # alias the countries lookup id to avoid ambiguous references when joining
    countries_aliased = countries.withColumnRenamed("id", "country_id").alias("c")

    answers = (
        answers.alias("a")
        .join(countries_aliased, F.col("a.country_name") == F.col("c.name"), how="left")
        .select(
            F.col("a.id"), F.col("a.years_code"), F.col("a.years_code_pro"), F.col("c.country_id"), F.col("a.ed_level")
        )
    )

    return answers


def index_join_table(answers: DataFrame, join_table: DataFrame, column: str, alias: str, id_name: str) -> DataFrame:
    joined = (
        answers.select(F.monotonically_increasing_id().alias("answer_id"), F.explode(column).alias(alias))
        .join(join_table.withColumnRenamed("id", id_name).alias("j"), F.col(alias) == F.col("j.name"), how="left")
        .select("answer_id", F.col(f"j.{id_name}"))
    )

    return joined


# script
context = Context.from_argv(sys.argv)

raw_data = context.glue.create_dynamic_frame.from_catalog(
    database=context.database,
    table_name=context.input_table_name,
)
# convert to Spark
dataframe = raw_data.toDF()
# transform in Spark
dataframe = pretransform(dataframe)
countries = create_country(dataframe)
# create language and database tables
lang = create_from_union(dataframe, alias="language", left="LanguageHaveWorkedWith", right="LanguageWantToWorkWith")
db = create_from_union(dataframe, alias="database", left="DatabaseHaveWorkedWith", right="DatabaseWantToWorkWith")
# create answers table
raw_answers = create_answers(dataframe)
# index countries into answers
answers = index_countries(raw_answers, countries)
# create 4 join tables
lah = index_join_table(dataframe, join_table=lang, column="language_have_worked_with", alias="lang", id_name="language_id")  # fmt: skip
law = index_join_table(dataframe, join_table=lang, column="language_want_to_work_with", alias="lang", id_name="language_id")  # fmt: skip
dah = index_join_table(dataframe, join_table=db, column="database_have_worked_with", alias="db", id_name="database_id")
daw = index_join_table(dataframe, join_table=db, column="database_want_to_work_with", alias="db", id_name="database_id")
# write answers
# TODO: Write to SQL here
