import boto3


def get_ssm_parameter(name: str, client=None) -> str:
    ssm_client = boto3.client("ssm") or client

    response = ssm_client.get_parameter(Name=name, WithDecryption=True)
    return response["Parameter"]["Value"]
