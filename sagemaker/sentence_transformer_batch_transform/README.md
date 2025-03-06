# Sentence Transformer Batch Transform

This snippet allows using SentenceTransformer model with SageMaker batch transform. It works by providing additional
file (inference.py), which overloads the default code of the SageMaker Batch Transform container. The script needs to
be added to the archive, where the model is located. Model used in the example is `microsoft/MiniLM-L12-H384-uncased`,
which is the smallest sentence  transformer model available, but it can be replaced with any model from available ones. 

## Creating the Model

Pull the model from HuggingFace:

```bash
git lfs install
git clone https://huggingface.co/sentence-transformers/{{MODEL_NAME}}
```

Add inference script and requirements file (optionally) to `code` directory:

```bash
cp model/inference.py {{MODEL_NAME}}/code
cp model/requirement.txt {{MODEL_NAME}}/code
```

Create archive and store it on S3:

```bash
cd {{MODEL_NAME}}
tar zcvf {{MODEL_NAME}}.tar.gz *
aws s3 cp {{MODEL_NAME}}.tar.gz s3://bucket/models/
```

## Running

To run install requirements for triggering the script (locally or in SageMaker notebook) and run main file:

```bash
pip3 install -r local-requirements.txt
python3 run.py
```

## Roles
This example assumes correct roles on AWS are used and created, sometimes it is not available by default. To achieve this
use the ARN of role with all permissions as `role` variable (simply ARN as string is enough). The role needs following
policies managed by AWS:
* `AmazonSageMakerFullAccess`
* `AmazonS3FullAccess`

## Reusing Model

In `run.py` the code below creates new model, by building the image and uploading it to ECR. Once the image is created,
the model can be reused (models can be browsed in SageMaker console in section `Inference/Models`). Once model

```python
transformer = model.transformer(  # model is HuggingFaceModel instance
    instance_count=1,
    instance_type="ml.m4.xlarge",
    output_path="s3://some-bucket/outputs/",
    strategy="SingleRecord",
    assemble_with="Line",
    max_payload=100,
)
```

To reuse the model find the name given to it while creating (given as parameter of `HuggingFaceModel` class, when not
given SageMaker will assign default name) and pass it to `model.transformer` method:

```python
transformer = model.transformer(  # model is HuggingFaceModel instance
    model_name=MODEL_NAME,  # must be created before
    instance_count=1,
    instance_type="ml.m4.xlarge",
    output_path="s3://some-bucket/outputs/",
    strategy="SingleRecord",
    assemble_with="Line",
    max_payload=100,
)
```

## Resources

| Name                             | Type          | Link                                                                                                                    |
|----------------------------------|---------------|-------------------------------------------------------------------------------------------------------------------------|
| Sentence Transformers            | Documentation | [LINK](https://www.sbert.net/)                                                                                          |
| Sentence Transformers            | Documentation | [LINK](https://huggingface.co/sentence-transformers)                                                                    |
| AWS SageMaker with Custom Script | Blog          | [LINK](https://aws.amazon.com/blogs/machine-learning/hugging-face-on-amazon-sagemaker-bring-your-own-scripts-and-data/) |
| AWS SageMaker SDK                | Documentation | [LINK](https://sagemaker.readthedocs.io/en/stable/)                                                                     |
