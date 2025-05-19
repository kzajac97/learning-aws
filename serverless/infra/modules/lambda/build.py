import argparse
import json
import os
import shutil
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Parse source, target, and shared paths.")
    parser.add_argument("--source", required=True, help="Path to source code")
    parser.add_argument("--target", required=True, help="Path to target build directory")
    parser.add_argument("--shared", required=True, help="Path(s) to shared code")

    args = parser.parse_args()
    return args.source, args.target, args.shared


if __name__ == "__main__":
    source, target, shared = parse_args()
    source = Path(source)
    target = Path(target)
    shared = json.loads(shared)

    print(f"Building lambda function from {source} path")
    print("Step 1: Copying source code to target directory")
    shutil.copytree(source, target, dirs_exist_ok=True)

    print(f"Step 2: Copying shared code to target directory: {shared}")
    for path in shared:
        shutil.copytree(path, target, dirs_exist_ok=True)

    print("Step 3: Running pip install")
    if (target / "requirements.txt").exists():
        os.system(f"pip3 install -r {target}/requirements.txt --target {target} --quiet")

    print(f"Building lambda from {source} completed!")
