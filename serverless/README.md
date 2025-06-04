# Serverless

This application is example IoT processing application using AWS Lambda, DynamoDB and Step-Functions. The application
has number of features and is deployed using terragrunt with parameterized configuration.

### Components

1. Sensor Lambda - function is an example of IoT ingest from remote sensor, doing simple calculation
2. SQS - communication layer between sensor and analytics module
3. Analytics - step-function processing inputs from SQS and computing moving-averages in time, uses 2 Lambda functions
4. DynamoDB - storage for broken sensors, used by sensor lambda
5. Trigger Sensor Script - script simulating real-world data generating process, by sending requests with random inputs with random intervals
6. Terraform Lambda Module - generic IaC set-up for Lambda functions, used by all Lambda functions in the application
7. Terragrunt - IaC orchestrator for terraform using configuration parameterized by YAML files to deploy `dev` and `prod` environments

# Sensor Lambda

Sensor Lambda is an example function, which simulates endpoint for receiving measurements from IoT sensor network. Each
measurement is simulating the resistance on termo-resistor, allowing to compute the temperature for known coefficients 
following the Steinhart–Hart equation.

### Flow

The flow of function is the following:
1. Load input JSON.
2. Check `sensor_id` in DynamoDB with registry of broken sensors.
3. Check, if given input is in acceptable range and mark sensor as broken, when it is not.
4. Compute the Temperature using the simulation (equation below).
5. Write message to SQS.
6. Notify user by SNS, when unexpected status is encountered.
7. Return event with the status.

**Note**: Details on the values of temperature to meet given status are irrelevant, they should serve as an example.
Details values can be found directly in the code and changed, if needed.

### Simulation

To compute the temperature, sensor computes the following equation.

$$
\frac{1}{T} = a + bln(R)+c(lnR)^3
$$

$a$, $b$ and $c$ are constants specific for given material. Values assumed for the simulation are: $a = 1.40 \cdot 10^{-3}$,
$b=2.37 \cdot 10^{-4}$ and $9.90 \cdot 10^{-8}$.
