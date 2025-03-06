import logging
from typing import Any, Iterable

from sentence_transformers import SentenceTransformer

# logger name can be changed, this is used to find in CloudWatch easily
LOGGER = logging.getLogger("sagemaker.custom_inference_script")
MODEL_NAME = "microsoft/MiniLM-L12-H384-uncased"  # can be replaced


def model_fn(model_dir: str) -> Any:
    """Overloaded function used by SageMaker to load the model"""
    LOGGER.info(f"Loading the model from {model_dir}")
    model = SentenceTransformer(f"{model_dir}/{MODEL_NAME}")
    return model


def predict_fn(data: dict, model: Any) -> dict[str, Iterable[float]]:
    """Overloaded function used by SageMaker to perform inference"""
    LOGGER.debug(f"Running inference on {len(data)} sentences")

    sentences = data.pop("inputs", data)
    embeddings = model.encode(sentences, convert_to_tensor=False, batch_size=32).mean(axis=0)

    return {"embeddings": embeddings.tolist()}
