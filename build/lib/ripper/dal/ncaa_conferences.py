import uuid

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError, ParamValidationError

from ripper.dal.logger import logger
from ripper.dal.tables import get_table, table_exists


class Conferences:
    table_name: str = "ncaa_conferences"
    dyn_resource: boto3.resource = None
    table: any = None

    def create_conference(self, conference_name):
        """
        Create a conference

        :param conference_name:
        :return:
        """
        conference_id = str(uuid.uuid4())  # Generate a UUID for the conference_id
        try:
            if self.conference_exists_by_name(conference_name):
                return

            self.table.put_item(
                Item={
                    "id": conference_id,
                    "name": conference_name,
                },
                ConditionExpression=Attr("name").not_exists(),
            )
        except ClientError as e:
            print(f"Error creating conference: {e.response['Error']['Message']}")
            raise

        except ParamValidationError as e:
            print(f"Error creating conference: {e}")
            raise

    def get_conference(self, conference_id):
        """
        Get a conference by its conference_id

        :param conference_id:
        :return:
        """
        try:
            response = self.table.get_item(Key={"conference_id": conference_id})
            return response.get("Item")
        except ClientError as e:
            print(f"Error getting conference: {e.response['Error']['Message']}")
            raise

    def get_conference_by_name(self, conference_name: str):
        """
        Get a conference by its name

        :param conference_name:
        :return:
        """
        try:
            response = self.table.scan(
                FilterExpression="#name = :name",
                ExpressionAttributeNames={"#name": "name"},
                ExpressionAttributeValues={":name": conference_name},
            )
            return response.get("Items", [])
        except ClientError as e:
            print(f"Error getting conference: {e.response['Error']['Message']}")
            raise

    def conference_exists_by_name(self, conference_name):
        """
        Check if a conference name exists in the table

        :param conference_name:
        :return:
        """
        try:
            items = self.get_conference_by_name(conference_name)
            return len(items) > 0
        except ClientError as e:
            print(
                f"Error checking if conference name exists: {e.response['Error']['Message']}"
            )
            raise

    def update_conference(
        self, conference_id, update_expression, expression_attribute_values
    ):
        """
        Update a conference by its ID

        :param conference_id:
        :param conference_data:
        :return:
        """
        try:
            self.table.update_item(
                Key={"id": conference_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
            )
        except ClientError as e:
            print(f"Error updating conference: {e.response['Error']['Message']}")

    def delete_conference(self, conference_id):
        """
        Delete a conference by its ID

        :param conference_id:
        :return:
        """
        try:
            self.table.delete_item(Key={"id": conference_id})
        except ClientError as e:
            print(f"Error deleting conference: {e.response['Error']['Message']}")
            raise

    def delete_conference_by_name(self, conference_name):
        """
        Delete a conference by its name

        :param conference_name:
        :return:
        """
        try:
            items = self.get_conference_by_name(conference_name)
            if items:
                for item in items:
                    self.table.delete_item(Key={"id": item.get("id")})
        except ClientError as e:
            print(f"Error deleting conference: {e.response['Error']['Message']}")

    @staticmethod
    def create_table(dyn_resource: boto3.resource, table_name: str):
        """
        Creates an Amazon DynamoDB table for storing conference data.
        The table uses the conference_id as the partition key.

        :param dyn_resource: A Boto3 DynamoDB resource.
        :param table_name: The name of the table to create.
        :return: The newly created table.
        """
        try:
            if table_exists(dyn_resource, table_name):
                return

            table = dyn_resource.create_table(
                TableName=table_name,
                KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "id", "AttributeType": "S"},
                    {"AttributeName": "name", "AttributeType": "S"},
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "name-index",
                        "KeySchema": [
                            {"AttributeName": "name", "KeyType": "HASH"},
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 10,
                            "WriteCapacityUnits": 10,
                        },
                    },
                ],
            )
            table.wait_until_exists()
        except ClientError as err:
            logger.error(
                "Couldn't create table %s. Here's why: %s: %s",
                table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

        return table


Conferences.table_name = "ncaa_conferences"
Conferences.dyn_resource = boto3.resource("dynamodb")

if table_exists(Conferences.dyn_resource, Conferences.table_name):
    Conferences.table = get_table(Conferences.dyn_resource, Conferences.table_name)
else:
    Conferences.table = Conferences.create_table(
        Conferences.dyn_resource, Conferences.table_name
    )


if __name__ == "__main__":
    conferences = Conferences()

    conferences.create_conference("SEC")
    conferences.create_conference("ACC")
    conferences.create_conference("Big Ten")

    print(conferences.get_conference_by_name("SEC"))
    print(conferences.get_conference_by_name("ACC"))
    print(conferences.get_conference_by_name("Big Ten"))
