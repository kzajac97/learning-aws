# AWS SageMaker Snippets

This repository contains snippets for model usage with AWS SageMaker.

**Examples**:

* `processing_job` - Example Docker container running `torchvision` for image augmentation
* `real_time_inference_endpoint` - Terraform code for deploying HuggingFace model to real-time endpoint using DeepLearning Containers
* `sentence_transformer_batch_transform` - Batch transform with Sentence Transformer
* `serverless_inference_endpoint` - Serverless inference endpoint with text generation model from HuggingFace

## Inference

AWS SageMaker offers 4 methods of deploying models (examples are added to this repository):

* [Real-time inference](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints.html)
* [Asynchronous inference](https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html)
* [Serverless inference](https://docs.aws.amazon.com/sagemaker/latest/dg/serverless-endpoints.html)
* [Batch inference](https://docs.aws.amazon.com/sagemaker/latest/dg/batch-transform.html)

### Real Time Endpoint

Real time inference is the simplest deployment mechanism in AWS SageMaker, it creates a machine (or a number of them,
since it also supports autoscaling), which listens to invocations and returns responses in real-time, executing them
with minimal latency. One or more models can be hosted in such an endpoint, even using different containers or SageMaker
pipelines. Autoscaling for endpoint instances can add the number of machines dynamically, as a response to changing
workload (both upscaling and downscaling).

This method of deployment is probably easiest to use, but is also most expansive, since the model is alive 24/7, often
requiring big and expansive machines to run.

### Serverless Inference

Serverless inference is an endpoint that is created on-demand and is charged per inference. It is build on top of AWS
Lambda. This deployment method is best for low traffic endpoints, where the response time is not critical, but needs to
be reasonably fast. It is also useful for models with peak traffic, where it is not worth to keep the endpoint running
24/7.

Maximal RAM for serverless inference is 6 GB, which is not too big. Concurrency (which is probably working the same way
as in AWS Lambda) can be set to 200, which means 200 parallel requests can be triggered without throttling.

Metric is added to AWS CloudWatch automatically, which allows monitoring over-head latency, which is called `OverheadLatency`.
Provisioned concurrency can be used to keep the endpoint warm, which means that the latency will be lower, which works
similarly regular to AWS Lambda.

### Batch Transform

Batch transform is used to run model with inputs stored on S3 and outputs send to S3. It is most useful for large
datasets, when the response does not need to be in real-time. Inputs and outputs are stored in JSON lines files.

Batch transform uses multi-model container under the hood, which means that it can run multiple models in parallel. The
serving component of multi-model server is written in Java, and it is open source (see: [https://github.com/awslabs/multi-model-server](https://github.com/awslabs/multi-model-server)).
It means, that running a batch transform on a single instance with 4 vCPUs will run 4 copies of the model in parallel
and aggregate the results. Moreover, batch transform can handle running multiple machines in a single job, for which
it is best to split the json-lines file into multiple smaller ones to easily associate the results with the inputs.

For generating embeddings or text responses, it is easy to run into the MMS response limits, which can be controlled
using environment variables. Usually, `torch-serving` is also used under the hood, for more details refer to the documentation
(see: [https://pytorch.org/serve/](https://pytorch.org/serve/)). MMS container can be extended to use custom models, but
it is usually easiest to add code dynamically, while using HuggingFace (as in the example with `inference.py` file).

### Resources

| Name               | Link                                                               |
|--------------------|--------------------------------------------------------------------|
| SageMaker examples | [LINK](https://github.com/aws/amazon-sagemaker-examples/tree/main) |
| SageMaker SDK      | [LINK](https://sagemaker.readthedocs.io/en/stable/)                |
