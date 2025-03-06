# Real Time Inference Endpoint

This example creates real time inference endpoint using AWS SageMaker, with terraform. It can be used to deploy certain
HuggingFace model from the hub, using the IaC approach. To run the example, `terraform` and AWS access are needed.

# Deploying

Run `terraform` apply to create the endpoint and deploy the model:

```bash
cd real_time_inference_endpoint/infra  # assuming running from repo root
terraform init
terraform plan -out plan.out
terraform apply "plan.out"  # can take up to 15 minutes
```

# Running

To invoke endpoint, simple python script can be used. It is given in `invoke.py`

### Working Locally

It might be useful, to pull the docker image locally from AWS and try the model out before creating the endpoint
(which might be expansive, if using GPU). To pull image run following commands (required AWS access set-up):

```bash
export AWS_REGION="<<AWS_REGION>>"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin 763104351884.dkr.ecr.$AWS_REGION.amazonaws.com
# HuggingFace image used in the example
docker pull 763104351884.dkr.ecr.eu-central-1.amazonaws.com/huggingface-pytorch-inference:2.0.0-transformers4.28.1-cpu-py310-ubuntu20.04
```

Then image can be run and investigated locally, using `docker run` command and `curl` to send requests. For details go
to [https://docs.aws.amazon.com/deep-learning-containers/latest/devguide/deep-learning-containers-ec2-tutorials-inference.html](https://docs.aws.amazon.com/deep-learning-containers/latest/devguide/deep-learning-containers-ec2-tutorials-inference.html).

This assumes PORT and MODEL are exported to env variables.

```bash
curl -d '{"instances": ["text inputs"]}' -X POST http://127.0.0.1:$PORT/v1/models/$MODEL:predict
```

# Resources

| Name                        | Link                                                                                                                               |
|-----------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| SageMaker Terraform Example | [LINK](https://github.com/jckuester/terraform-sagemaker-example/blob/master/main.tf)                                               |
| DeepLearning Container      | [LINK](https://github.com/aws/deep-learning-containers)                                                                            |
| DeepLearning Container Docs | [LINK](https://docs.aws.amazon.com/deep-learning-containers/latest/devguide/deep-learning-containers-ec2-tutorials-inference.html) |
| AWS SageMaker SDK           | [LINK](https://sagemaker.readthedocs.io/en/stable/)                                                                                |
| SageMaker AB Testing        | [LINK](https://docs.aws.amazon.com/sagemaker/latest/dg/model-ab-testing.html)                                                      |
| SageMaker Invoke Endpoint   | [LINK](https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_runtime_InvokeEndpoint.html)                                  |
