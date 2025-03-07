import os

import click
import torch
from torchvision import io
from torchvision.transforms import v2

EXTENSION = "JPEG"


@click.command()
@click.option("--input-dir", type=str, required=True, help="Directory with images to preprocess")
@click.option("--output-dir", type=str, required=True, help="Directory to save preprocessed images")
def main(input_dir: str, output_dir: str):
    transforms = v2.Compose(
        [
            v2.Resize(size=(224, 224), antialias=True),  # resize to standard size
            v2.RandomResizedCrop(size=(224, 224), antialias=True),
            v2.RandomHorizontalFlip(p=0.25),  # half of images is expected to be flipped by at least one axis
            v2.RandomVerticalFlip(p=0.25),
            v2.RandomRotation(degrees=45),
            v2.RandomGrayscale(p=0.1),
            v2.ToDtype(torch.float32, scale=True),
            v2.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    images = [io.read_image(f"{input_dir}/{path}") for path in os.listdir(input_dir) if path.endswith(EXTENSION)]
    transformed = [transforms(batch) for batch in images]

    torch.save(torch.cat(transformed), f"{output_dir}/images.pt")  # store as entire batch of tensors


if __name__ == "__main__":
    main()
