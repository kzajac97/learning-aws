# Learning AWS

This repository contains various project and smaller scripts related to learning AWS. Most of them has been created to
support the course at Wrocław University of Science and Technology, related to AWS and cloud computing.

Currently implemented applications:
* `backend` - configuration for shared terraform backend management with S3 and DynamoDB
* `data_processing` - example data processing app using AWS Glue and PySpark
* `sagamaker` - number of stand-alone SageMaker examples for inference and pre-processing
* `severless` - example serverless app for toy IoT data processing and analytics using AWS Lambda, DynamoDB and StepFunctions

### How this Works?

Each directory is small or medium-sized example application using selected AWS services. The details on architecture and
the learning purpose are documented in each README.md in the repositories. Additionally, specific README files contain
some background knowledge on AWS usage and some tips on reading order for the code and docs.

*Note*: It is recommended to start with main README and follow steps described in there alone.

### Backend and Actions

Larger applications use terraform to define AWS resources using IaC approach. One of the applications is the shared
backend configuration, which is used by all of those. This is the terraform backend and "global" services for the
account. GitHub actions use and require infrastructure defined by Backend application, so to use them, following the
set-up described in `backend/README.md` needs to be done first.

Currently, backend supports terraform S3 + DynamoDB for terraform state management and KMS definition for SOPS.

### AWS

The services were developed using AWS educational account with is provided by the University. It can be used with
personal accounts as well, but it would require manual IAM set-up. The education account uses single role `LabRole` with
all required permissions, which is not created anywhere in this repository. It is also used by CI/CD on GitHub.
