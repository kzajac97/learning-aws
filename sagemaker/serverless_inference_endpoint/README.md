# Serverless Inference Endpoint

This example creates serverless inference endpoint using SageMaker for [GALACTICA](https://huggingface.co/facebook/galactica-125m)
model (using mini version) for the task of generating citations for given text prompt.

## Creating Model

Pull the model from HuggingFace:

```bash
git clone https://huggingface.co/facebook/galactica-125m
```

Add inference script:

```bash
cd model
mkdir galactica-125m/code
cp inference.py galactica-125m/code/
```

Create archive and store it on S3:

```bash
tar zcvf galactica-citation-prediction.tar.gz *
aws s3 cp galactica-citation-prediction.tar.gz s3://bucket/models/
```

## Running

To run the example, you need to have AWS credentials configured and have SageMaker SDK installed. To use the endpoint
class provided in `endpoint.py` can be used, to create it run following code:

```python
endpoint = ServerlessEndpoint(
    model_name="{{MODEL_NAME}}",  # replace with model name visible in AWS
    model_dir="{{MODEL_DIR}}",  # replace with S3 URI of zipped model
    role_arn="{{ROLE_ARN}}",  # replace with ARN of role with SageMaker permissions
    env={},  # optional environment variables for model
)

# create endpoint
endpoint.setup()
# run inference
endpoint("The Transformer architecture")
# delete endpoint
endpoint.cleanup()
```

This repository also contains example notebook with usage of the custom serverless endpoint class. 

## Resources

| Name                     | Link                                                                              |
|--------------------------|-----------------------------------------------------------------------------------|
| Galactica                | [LINK](https://huggingface.co/facebook/galactica-125m)                            |
| Galactica                | [LINK](https://arxiv.org/abs/2211.09085)                                          |
| AWS SageMaker Serverless | [LINK](https://docs.aws.amazon.com/sagemaker/latest/dg/serverless-endpoints.html) |
| AWS SageMaker SDK        | [LINK](https://sagemaker.readthedocs.io/en/stable/)                               |
