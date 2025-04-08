import dataclasses
import re
import sys
from typing import Final

from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lit, size, split, when
from pyspark.sql.types import IntegerType


def camel_to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


# glue job parameters
GLUE_INPUTS: Final[list[str]] = [
    "JOB_NAME",
    "glue_database",
    "input_glue_table_name",
    "output_glue_table_name",
    "source_label",
]
# settings for ingest transformation
MAX_SPLIT_COL_ITEMS: Final[int] = 10
MULTI_VALUE_SEPARATOR: Final[str] = ";"
ED_LEVEL_REJECTED_VALUES: Final[tuple[str, ...]] = ("Something else",)
AGE_REJECTED_VALUES: Final[tuple[str, ...]] = ("Under 18 years old", "65 years or older", "Prefer not to say")
AGE_MAPPING: Final[dict[str, int]] = {"Less than 1 year": 0, "More than 50 years": 51}
# column names and rules
RAW_COLUMNS_TO_KEEP: Final[tuple[str, ...]] = (
    "Age",
    "YearsCode",
    "YearsCodePro",
    "Country",
    "EdLevel",
    "LanguageHaveWorkedWith",
    "DatabaseHaveWorkedWith",
    "LanguageWantToWorkWith",
    "DatabaseWantToWorkWith",
)
SPLIT_COLUMNS: Final[tuple[str, ...]] = (
    "LanguageHaveWorkedWith",
    "DatabaseHaveWorkedWith",
    "LanguageWantToWorkWith",
    "DatabaseWantToWorkWith",
)
INT_COLUMNS: Final[tuple[str, ...]] = ("YearsCode", "YearsCodePro", "Age")


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
        parameters = getResolvedOptions(argv, GLUE_INPUTS)

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


def transform(data: DataFrame, context: Context) -> DataFrame:
    # step 1: drop unwanted columns and nans
    data = data.select(list(RAW_COLUMNS_TO_KEEP))  # PySpark can only work with list columns, not tuples
    data = data.na.drop()

    # step 2: filter out rows where the count of languages/databases is 10 or more
    for split_column in SPLIT_COLUMNS:
        data = data.filter(size(split(col(split_column), MULTI_VALUE_SEPARATOR)) < MAX_SPLIT_COL_ITEMS)

    # step 3: remove rows with specific education and age outliers
    data = data.filter(~col("EdLevel").isin(list(ED_LEVEL_REJECTED_VALUES)))
    data = data.filter(~col("Age").isin(list(AGE_REJECTED_VALUES)))

    # step 4: map age values
    for age, mapped_age in AGE_MAPPING.items():
        data = data.withColumn("Age", when(col("Age") == age, mapped_age).otherwise(col("Age")))

    # step 5: cast numeric columns to integer
    for cast_column in INT_COLUMNS:
        data = data.withColumn(cast_column, col(cast_column).cast(IntegerType()))

    # step 6: split multi-value columns
    for split_column in SPLIT_COLUMNS:
        data = data.withColumn(split_column, split(col(split_column), MULTI_VALUE_SEPARATOR))

    # step 7: add a partition column with constant value -> the source year of the data
    data = data.withColumn("source_year", lit(context.source_label))

    # step 8: map column from CamelCase to snake_case
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
dataframe = transform(dataframe, context)
# convert back to Glue DynamicFrame
transformed_data = DynamicFrame.fromDF(dataframe, context.glue, "transformed_data")

context.glue.write_dynamic_frame.from_catalog(
    frame=transformed_data,
    database=context.database,
    table_name=context.output_table_name,
)
