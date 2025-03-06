import boto3

client = boto3.client("sagemaker-runtime")


if __name__ == "__main__":
    # from https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_runtime_InvokeEndpoint.html
    custom_attributes = "c000b4f9-df62-4c85-a0bf-7c525f9104a4"  # An example of a trace ID.
    endpoint_name = "test-endpoint"  # Your endpoint name.
    content_type = "json"  # The MIME type of the input data in the request body.
    accept = "json"  # The desired MIME type of the inference in the response.
    payload = "Test question"

    response = client.invoke_endpoint(
        EndpointName=endpoint_name,
        CustomAttributes=custom_attributes,
        ContentType=content_type,
        Accept=accept,
        Body=payload
    )

    print(response)
