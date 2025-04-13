# Data Processing

## Glue

AWS Glue is a ETL services, allowing to connect to various data sources and run ETL jobs in PySpark without managing
the underlying infrastructure. Glue fundamentally consists of three concepts:
* Data Catalog - metadata store with table definitions and control information (no physical data is stored)
* Crawlers - programs for connecting to the data sources, they can infer schema and create table definitions in Data Catalog
* Jobs - ETL jobs, which are the actual workers, written in Spark, which is extended by AWS Glue with extra features

### Glue Workers

AWS Glue is priced mostly based on DPU (data-processing-unit) runtime. DPUs are used for crawlers and ETL jobs, where
the size of the machine is counted as multiples of DPU. The options range from `G.025X` (1/4 DPU), to standard `G.1X`
and up to `G.8X` with 32 vCPUs and 128GB of memory. 

AWS Glue ETL can be written is Python or Scala, where python scripts need to be based on PySpark. Binary supported
libraries, such as pandas or numpy are not supported.

## Resources

* https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html
