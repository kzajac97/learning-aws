# no need for docker build, just TAG and push to ECR existing container
# this example uses default CPU torch container
FROM pytorch/pytorch:latest

# install python packages
RUN pip install --upgrade pip
RUN pip install --no-cache-dir click==8.1.6

ENTRYPOINT ["python3", "/main.py"]
