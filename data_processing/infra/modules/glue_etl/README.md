# Glue ETL Module

This module creates AWS Glue ETL job parameterized with script path and standard Glue configuration. The module assumes
using python and Glue `5.0`.

Script is uploaded to `glue_assets_bucket` under a key given by the filename of the script.
