import logging

import torch
from transformers import AutoTokenizer, OPTForCausalLM

# logger name can be changed, this is used to find in CloudWatch easily
LOGGER = logging.getLogger("sagemaker.custom_inference_script")
MODEL_NAME = "facebook/galactica-125m"  # can be replaced


def model_fn(model_dir: str) -> tuple:
    LOGGER.info(f"Loading the model from {model_dir}")
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = OPTForCausalLM.from_pretrained(model_dir)
    return model, tokenizer


def predict_fn(data: dict[str, str], model_and_tokenizer: tuple) -> str:
    model, tokenizer = model_and_tokenizer
    input_text = data["inputs"] + " " + "[START_REF]"  # add special citation token

    inputs = tokenizer(input_text, return_tensors="pt")
    tokens = inputs["input_ids"]

    with torch.no_grad():
        outputs = model.generate(inputs["input_ids"])

    # remove input text by slicing and decode without special tokens
    citation = tokenizer.decode(outputs.squeeze()[len(tokens.squeeze()) :], skip_special_tokens=True)
    return citation.translate(str.maketrans("", "", "\n\t\r")).strip()  # remove newlines and trailing spaces
