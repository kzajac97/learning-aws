import dataclasses
import re
import sys

from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, size, split
from pyspark.sql.types import IntegerType


def camel_to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


# transformation settings
# columns to split into arrays
COLUMNS_TO_SPLIT = [
    "LanguageHaveWorkedWith",
    "DatabaseHaveWorkedWith",
    "LanguageWantToWorkWith",
    "DatabaseWantToWorkWith",
]
# column names and rules
RAW_COLUMNS_TO_KEEP = [
    "YearsCode",
    "YearsCodePro",
    "Country",
    "EdLevel",
    "LanguageHaveWorkedWith",
    "DatabaseHaveWorkedWith",
    "LanguageWantToWorkWith",
    "DatabaseWantToWorkWith",
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
    output_table_name: str
    source_label: str

    @classmethod
    def from_argv(cls, argv: dict):
        glue_inputs = ["JOB_NAME", "glue_database", "input_glue_table_name", "output_glue_table_name", "source_label"]
        parameters = getResolvedOptions(argv, glue_inputs)

        return cls(
            spark=SparkContext.getOrCreate(),
            glue=GlueContext(SparkContext.getOrCreate()),
            glue_job=Job(GlueContext(SparkContext.getOrCreate())),
            job_name=parameters["JOB_NAME"],
            database=parameters["glue_database"],
            input_table_name=parameters["input_glue_table_name"],
            output_table_name=parameters["output_glue_table_name"],
            source_label=parameters.get("source_label", "default"),
        )


def transform(data: DataFrame) -> DataFrame:
    # step 1: drop unwanted columns and nans
    data = data.select(RAW_COLUMNS_TO_KEEP)  # PySpark can only work with list columns, not tuples
    data = data.replace("NA", None).replace("", None)
    data = data.na.drop(how="any")

    # step 2: filter out rows where the count of languages/databases is 10 or more
    for split_column in COLUMNS_TO_SPLIT:
        data = data.filter(size(split(col(split_column), ";")) < 10)

    # step 3: remove rows with specific education and age outliers
    data = data.filter(~col("EdLevel").isin(["Something else"]))

    # step 4: cast numeric columns to integer
    for cast_column in ("YearsCode", "YearsCodePro"):
        data = data.withColumn(cast_column, col(cast_column).cast(IntegerType()))

    # step 5: split multi-value columns
    for column in COLUMNS_TO_SPLIT:
        data = data.withColumn(column, split(col(column), ";"))

    # step 6: map column from CamelCase to snake_case
    data = data.toDF(*[camel_to_snake(column) for column in data.columns])

    return data


# script
context = Context.from_argv(sys.argv)

raw_data = context.glue.create_dynamic_frame.from_catalog(
    database=context.database,
    table_name=context.input_table_name,
)
# convert to Spark
dataframe = raw_data.toDF()
# transform in Spark
dataframe = transform(dataframe)
# convert back to Glue DynamicFrame
transformed_data = DynamicFrame.fromDF(dataframe, context.glue, "transformed_data")

context.glue.write_dynamic_frame.from_catalog(
    frame=transformed_data,
    database=context.database,
    table_name=context.output_table_name,
)
