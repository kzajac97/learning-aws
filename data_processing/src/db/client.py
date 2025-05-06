import boto3
import psycopg2
from psycopg2 import sql


def get_ssm_parameter(name: str, client=None) -> str:
    ssm_client = client or boto3.client("ssm")

    response = ssm_client.get_parameter(Name=name, WithDecryption=True)
    return response["Parameter"]["Value"]


class DBClient:
    """
    PostgreSQL manager for simple queries to support health-check script to verify the processing output.
    """

    def __init__(self, host: str, name: str, user: str, password: str, port: str = "5432"):
        self.host = host  # RDS endpoint
        self.name = name
        self.user = user
        self.password = password
        self.port = port

        self.connection = None

    @classmethod
    def from_ssm(cls, prefix: str, client):
        endpoint = get_ssm_parameter(f"/{prefix}/endpoint", client)
        host, port = endpoint.split(":")
        return cls(
            host=host,
            name=get_ssm_parameter(f"/{prefix}/name", client),
            user=get_ssm_parameter(f"/{prefix}/user", client),
            password=get_ssm_parameter(f"/{prefix}/password", client),
            port=port,
        )

    @property
    def jdbc_url(self):
        return f"jdbc:postgresql://{self.host}:{self.port}/{self.name}"

    @property
    def jdbc_connection(self) -> dict:
        return {
            "user": self.user,
            "password": self.password,
            "driver": "org.postgresql.Driver",
        }

    def connect(self):
        self.connection = psycopg2.connect(
            host=self.host,
            database=self.name,
            user=self.user,
            password=self.password,
            port=self.port,
        )

    def execute(self, sql: str):
        if self.connection is None:
            self.connect()

        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            self.connection.commit()

    def select(self, table: str, limit: int | None = None) -> list[tuple]:
        if self.connection is None:
            self.connect()

        with self.connection.cursor() as cursor:
            query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table))
            if limit:
                query += sql.SQL(" LIMIT {}").format(sql.Placeholder())
                cursor.execute(query, (limit,))
            else:
                cursor.execute(query)

            return cursor.fetchall()

    def list_tables(self) -> list[str]:
        if self.connection is None:
            self.connect()

        try:
            with self.connection.cursor() as cursor:
                query = sql.SQL("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                cursor.execute(query)
                return [row[0] for row in cursor.fetchall()]
        except psycopg2.Error as e:
            self.connection.rollback()  # Roll back the transaction
            raise e  # Re-raise the exception to h00andle it appropriately

    def get_column_names(self, table: str) -> list[str]:
        if self.connection is None:
            self.connect()

        try:
            with self.connection.cursor() as cursor:
                query_str = "SELECT column_name FROM information_schema.columns WHERE table_name = %s"
                query = sql.SQL(query_str).format(sql.Placeholder())
                cursor.execute(query, (table,))
                return [row[0] for row in cursor.fetchall()]
        except psycopg2.Error as e:
            self.connection.rollback()
            raise e
