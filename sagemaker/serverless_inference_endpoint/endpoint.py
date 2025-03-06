import logging
from typing import Optional

from sagemaker.huggingface.model import HuggingFaceModel
from sagemaker.serverless import ServerlessInferenceConfig


class ServerlessEndpoint:
    def __init__(self, model_name: str, model_dir: str, role_arn: str, env: Optional[dict] = None):
        self.model_name = model_name
        self.model_dir = model_dir
        self.role_arn = role_arn
        self.env = env or {}

        self.predictor = None
        self.logger = logging.getLogger(__name__)

    def setup(self) -> None:
        """
        Creates the Serverless endpoint with Galactica model
        Uses hard-coded values with 6GB memory size and 10 max concurrency (just an example!)
        """
        model = HuggingFaceModel(
            name=self.model_name,
            model_data=self.model_dir,
            env=self.env,
            role=self.role_arn,
            transformers_version="4.26.0",
            pytorch_version="1.13.1",
            py_version="py39",
        )

        serverless_config = ServerlessInferenceConfig(
            memory_size_in_mb=6144,  # maximal memory size in MB for serverless endpoint
            max_concurrency=1,  # can be up to 200
        )

        self.predictor = model.deploy(serverless_inference_config=serverless_config)
        self.logger.info("Created endpoint!")

    def cleanup(self) -> None:
        """Removes the endpoint and model from SageMaker"""
        if self.predictor:
            self.predictor.delete_model()
            self.predictor.delete_endpoint()
            self.logger.info("Cleaned up endpoint!")
        else:
            self.logger.warning("Nothing to clean up!")

    def __call__(self, text: str) -> str:
        """Predicts citation for given text using the endpoint and returns model response as text"""
        if self.predictor:
            return self.predictor.predict({"inputs": text})
        else:
            self.logger.error("Endpoint not set up!")
            raise RuntimeError("Endpoint not set up!")
