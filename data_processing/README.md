# Data Processing

This application is a toy example of Glue based data processing application, using StackOverflow developer survey as
exemplary data. The app contains set-up for transforming raw CSV with survey data for particular year into normalized
SQL database, hosted on Amazon RDS. All transformations are done in PySpark and can be run as Glue jobs.

Application layout:
* `infra`
  * `database.tf` - Amazon RDS set-up
  * `glue.tf` - AWS Glue Data Catalog and Glue Crawler set-up
  * `ingest.tf` - AWS Glue ETL job for transforming raw data into structured schema and storing it in Glue Data Catalog
  * `network.tf` - VPC and security group set-up for RDS
  * `transform.tf` - AWS Glue ETL job for transforming raw data into normalized schema
* `src`
  * `db` - PostgreSQL database client and SQL script with table definitions and local PySpark script for data insertion
  * `glue` - PySpark scripts source code
  * `workflow.ipynb` - Jupyter notebook with example workflow for running the app using python scripts

*Note*: Transforming such data in normalized schema is not usually done, this application is meant as example showcasing
AWS Glue, Athena and PySpark for educational purpose. In real-world case analytical schema would be probably better,
Stack Overflow data could be also easily analysed using just Glue Crawler + Athena setup. PySpark might also be overkill
for such small dataset.

## AWS Glue

AWS Glue is a ETL services, allowing to connect to various data sources and run ETL jobs in PySpark without managing
the underlying infrastructure. Glue fundamentally consists of three concepts:
* Data Catalog - metadata store with table definitions and control information (no physical data is stored)
* Crawlers - programs for connecting to the data sources, they can infer schema and create table definitions in Data Catalog
* Jobs - ETL jobs, which are the actual workers, written in Spark, which is extended by AWS Glue with extra features

All those components are used in this applications, Data Catalog is used to store data definitions with different degree
of processing, firstly using Glue Crawler to infer schema from raw CSV files, then using Glue ETL job to transform the
data into structured parquet files, and finally using another Glue ETL job to transform the data into normalized schema.

Final step is done locally, to show RDS connection and PySpark also locally.

### Glue Workers

AWS Glue is priced mostly based on DPU (data-processing-unit) runtime. DPUs are used for crawlers and ETL jobs, where
the size of the machine is counted as multiples of DPU. The options range from `G.025X` (1/4 DPU), to standard `G.1X`
and up to `G.8X` with 32 vCPUs and 128GB of memory.

AWS Glue ETL can be written is Python or Scala, where python scripts need to be based on PySpark. Binary supported
libraries, such as pandas or numpy are not supported.

## AWS Athena

AWS Athena is a serverless query engine, which allows to run SQL queries on data stored in S3. It uses Glue Data Catalog
as a metadata store, and can be used to query data stored in various formats, such as CSV, JSON, Parquet or ORC. Athena
is based on Presto, which is an open-source distributed SQL query engine. It is a serverless service, so there is no need
to manage the underlying infrastructure. Athena is charged based on the amount of data scanned.

In this applications Athena is used to query and look around the data on different levels of processing, apart from the
last step, where data is in PostgreSQL database.

## VPC & Security Groups

In this application VPC is used to host the RDS database. The VPC is set up with public and private subnets, where the
`default` VPC for AWS Account is used. The RDS database is hosted in the private subnet and approach of IP whitelisting
is used to allow access to the database from the Glue jobs. The security group is set up to allow access from single IP
given as terraform variable.

*Note*: If using the copy of this infrastructure, set the IP to desired address, ideally under the University VPN, which
will prevent access from outside this network to the RDS. This is educational example, so strict security is not
required. In production use cases IP whitelisting is not advised as safety gold standard.

## Resources

* https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html
* https://docs.aws.amazon.com/glue/latest/dg/catalog-and-crawler.html
* https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html
