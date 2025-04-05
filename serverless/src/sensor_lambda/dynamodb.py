from botocore.exceptions import ClientError


class SensorRegistryClient:
    def __init__(self, client, table_name: str):
        self.client = client
        self.table_name = table_name

    def put_item(self, sensor_id: str, working_ok: bool):
        self.client.put_item(
            TableName=self.table_name, Item={"sensor_id": {"S": sensor_id}, "working_ok": {"BOOL": working_ok}}
        )

    def get_item(self, sensor_id: str) -> dict:
        response = self.client.get_item(TableName=self.table_name, Key={"sensor_id": {"S": sensor_id}})
        item = response.get("Item", {})
        return {k: (v["S"] if "S" in v else v["BOOL"]) for k, v in item.items()}

    def update_item(self, sensor_id: str, working_ok: bool):
        self.client.update_item(
            TableName=self.table_name,
            Key={"sensor_id": {"S": sensor_id}},
            UpdateExpression="set working_ok = :w",
            ExpressionAttributeValues={":w": {"BOOL": working_ok}},
        )

    def exists(self, sensor_id: str) -> bool:
        try:
            response = self.client.get_item(
                TableName=self.table_name, Key={"sensor_id": {"S": sensor_id}}, ProjectionExpression="sensor_id"
            )
            return "Item" in response
        except ClientError:  # sensor_id not found - avoid scan
            return False
