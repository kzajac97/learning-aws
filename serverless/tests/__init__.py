import sys

# all lambda modules are on sys.path to allow imports the same way as in the lambda functions on AWS
sys.path.append("src/reporter_lambda")
sys.path.append("src/receiver_lambda")
sys.path.append("src/sensor_lambda")
