from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput


INPUT_DIR = "/opt/ml/processing/input/"
OUTPUT_DIR = "/opt/ml/processing/output"

AWS_ACCOUNT_ID = "<<AWS_ACCOUNT_ID>>"
AWS_REGION = "<<AWS_REGION>>"
ROLE_ARN = "<<ROLE_ARN>>"


if __name__ == "__main__":
    script_processor = ScriptProcessor(
        command=["python3"],
        image_uri=f"{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/torchvision:latest",
        role=ROLE_ARN,  # assumes using ARN of role with all permissions for SageMaker
        instance_count=1,
        instance_type="ml.t3.medium",  # small CPU machine
    )

    script_processor.run(
        code="container/main.py",  # references the script in the local machine, not the container
        inputs=[ProcessingInput(source="s3://dataset/images/", destination=INPUT_DIR)],  # example S3 URI
        outputs=[ProcessingOutput(source=OUTPUT_DIR, destination="s3://dataset/tensors/")],  # example S3 URI
        arguments=[f"--input-dir={INPUT_DIR}", f"--output-dir={OUTPUT_DIR}"],
    )
