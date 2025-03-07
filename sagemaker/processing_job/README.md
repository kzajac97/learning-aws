# Processing Job

AWS SageMaker can be used to implement data processing jobs, which can be data cleaning, feature engineering, validation
or any other data processing task. SageMaker can run Spark jobs (including scripts written with PySpark), scikit-learn
jobs and custom scripts, written using framework processors (with HuggingFace supported) or custom containers.

## Container

In this example, the preprocessing is done using torchvision, to get such container, it can be pushed to ECR. The
simple example is give by `Dockerfile` is stored in `container` directory, to create the image following command
can be used:

```bash
export IMAGE_NAME="torchvision"

cd container
docker build -t $IMAGE_NAME .
```

Alternatively, pulling torch from Docker Hub should be enough, since only standard packages are used:

```bash
docker pull pytorch/pytorch:latest
```

To add docker to ECR use following commands:

```bash
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com  # assume AWS variables are exported
aws ecr create-repository --repository-name $IMAGE_NAME
docker tag $IMAGE_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE_NAME:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE_NAME:latest
```

After executing those commands, the single image with `latest` tag should be available in ECR repository with the name
given by `$IMAGE_NAME`.

## Augmentation

In this example batch of images is augmented using pure PyTorch. This has a number of use-cases, such as preprocessing
to prevent adversarial attacks during inference or augmentation of images during training, to improve the model.
Moreover, using SageMaker processing job augmentation can be quite easily decoupled and run on smaller CPU machines
(`ml.t3.medium` used in example has 2 vCPU and 4 GiB of memory), to reduce load on the larger GPU, where training is run.

## Running

Defining script processor requires machine parameters (instance type and number of instances), image URI and AWS IAM
role. Running the script processing job downloads the data from S3 to given by (controlled by source and destination
parameters of `ProcessingInput`), runs code given by `code.py` parameter, which is downloaded to container and uploads 
the results from container to S3 (controlled by parameters of `ProcessingOutput`). 

To run job in standalone way use following code snippet adding required parameters:

```python
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput


script_processor = ScriptProcessor(
    command=["python3"],
    image_uri=f"{ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/torchvision:latest",
    role=ARN,  # assumes using ARN of role with all permissions
    instance_count=1,
    instance_type="ml.t3.medium"  # small CPU machine
)

script_processor.run(
    code="main.py",
    inputs=[ProcessingInput(source="s3://dataset/train/", destination="/opt/ml/processing/input")],
    outputs=[ProcessingOutput(source="/opt/ml/processing/output")])
```

To launch batch processing job on single training batch during training following snippet can be used:

```python
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput

BATCH_SIZE = 128  # assume batch size is given during script
script_processor = ScriptProcessor(
    command=["python3"],
    image_uri=f"{ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/torchvision:latest",
    role=ARN,  # assumes using ARN of role with all permissions
    instance_count=1,
    instance_type="ml.t3.medium"  # small CPU machine
)


for index in range(0, len(input_paths), BATCH_SIZE):  # batching of paths to input images
    batch = input_paths[index : index + BATCH_SIZE]
    
    input_dir = f"s3://dataset/train/{index}/"
    output_dir = f"s3://dataset/preprocessed/{index}/"
    
    
    script_processor.run(
        code="main.py",
        inputs=[ProcessingInput(source="s3://dataset/train/", destination="/opt/ml/processing/input")],
        outputs=[ProcessingOutput(source="/opt/ml/processing/output")],
        arguments=[f"--input-dir={input_dir}", f"--output-dir={output_dir}"]  # needs to handle arguments in script
    )
```

## Resources

| Name                          | Link                                                                                                                                      |
|-------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| SageMaker Processing Job Docs | [LINK](https://docs.aws.amazon.com/sagemaker/latest/dg/processing-job.html)                                                               |
| AWS Examples                  | [LINK](https://github.com/aws/amazon-sagemaker-examples/tree/main/sagemaker_processing/scikit_learn_data_processing_and_model_evaluation) |
| PyTorch Augmentation          | [LINK](https://pytorch.org/vision/stable/transforms.html)                                                                                 |
| SageMaker Pricing             | [LINK](https://aws.amazon.com/sagemaker/pricing/)                                                                                         |

