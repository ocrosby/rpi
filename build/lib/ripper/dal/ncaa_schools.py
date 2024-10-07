import uuid

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError, ParamValidationError

from ripper.dal.logger import logger
from ripper.dal.tables import get_table, table_exists


class Schools:
    table_name: str = "ncaa_schools"
    dyn_resource: boto3.resource = None
    table: any = None

    def __init__(self):
        """
        Constructor for the Schools class
        :param dyn_resource: A Boto3 DynamoDB resource.
        """

    def create_school(self, school_name: str, conference_id: str = None):
        school_id = str(uuid.uuid4())  # Generate a UUID for the school_id
        try:
            if self.school_name_exists(school_name):
                return

            self.table.put_item(
                Item={
                    "id": school_id,
                    "name": school_name,
                    "conference_id": conference_id,
                },
                ConditionExpression=Attr("name").not_exists(),
            )
        except ClientError as e:
            print(f"Error creating school: {e.response['Error']['Message']}")
            raise

        except ParamValidationError as e:
            print(f"Error creating school: {e}")
            raise

    def get_schools(self) -> list[any]:
        """
        Get all schools
        :return:
        """
        try:
            response = self.table.scan()
            return response.get("Items", [])
        except ClientError as e:
            print(f"Error getting schools: {e.response['Error']['Message']}")
            raise

    def get_schools_by_conference(self, conference_id) -> list[any]:
        """
        Get schools by conference_id
        :param conference_id:
        :return:
        """
        try:
            response = self.table.scan(
                FilterExpression="#conference_id = :conference_id",
                ExpressionAttributeNames={"#conference_id": "conference_id"},
                ExpressionAttributeValues={":conference_id": conference_id},
            )
            return response.get("Items", [])
        except ClientError as e:
            print(
                f"Error getting schools by conference: {e.response['Error']['Message']}"
            )
            raise

    def get_school(self, school_id) -> any:
        """
        Get a school by its school_id

        :param school_id:
        :return:
        """
        try:
            response = self.table.get_item(Key={"school_id": school_id})
            return response.get("Item")
        except ClientError as e:
            print(f"Error getting school: {e.response['Error']['Message']}")
            raise

    def get_school_by_name(self, school_name) -> list[any]:
        """
        Get a school by its name

        :param school_name:
        :return:
        """
        try:
            response = self.table.scan(
                FilterExpression="#name = :name",
                ExpressionAttributeNames={"#name": "name"},
                ExpressionAttributeValues={":name": school_name},
            )
            return response.get("Items", [])
        except ClientError as e:
            print(f"Error getting school by name: {e.response['Error']['Message']}")
            raise

    def school_name_exists(self, school_name: str) -> bool:
        """
        Check if a school name exists

        :param school_name:
        :return:
        """
        try:
            school = self.get_school_by_name(school_name)
            return school is not None
        except ClientError as e:
            print(
                f"Error checking if school name exists: {e.response['Error']['Message']}"
            )
            raise

    def update_school(self, school_id, update_expression, expression_attribute_values):
        try:
            self.table.update_item(
                Key={"school_id": school_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
            )
        except ClientError as e:
            print(f"Error updating school: {e.response['Error']['Message']}")

    def delete_school(self, school_id):
        try:
            self.table.delete_item(Key={"school_id": school_id})
        except ClientError as e:
            print(f"Error deleting school: {e.response['Error']['Message']}")

    def delete_school_by_name(self, school_name):
        """
        Delete a school by its name

        :param school_name:
        :return:
        """
        try:
            items = self.get_school_by_name(school_name)
            if items:
                for item in items:
                    self.table.delete_item(Key={"id": item.get("id")})
        except ClientError as e:
            print(f"Error deleting school by name: {e.response['Error']['Message']}")
            raise

    def school_exists_by_name(self, school_name) -> bool:
        """
        Check if a school exists by its name

        :param school_name:
        :return:
        """
        try:
            items = self.get_school_by_name(school_name)
            return len(items) > 0
        except ClientError as e:
            print(f"Error checking if school exists: {e.response['Error']['Message']}")
            raise

    @staticmethod
    def create_table(dyn_resource: boto3.resource, table_name: str):
        """
        Creates an Amazon DynamoDB table for storing school data.
        The table uses the school_id as the partition key.

        :param dyn_resource: A Boto3 DynamoDB resource.
        :param table_name: The name of the table to create.
        :return: The newly created table.
        """
        try:
            table = dyn_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {"AttributeName": "id", "KeyType": "HASH"},  # Partition key
                ],
                AttributeDefinitions=[
                    {"AttributeName": "id", "AttributeType": "S"},
                    {"AttributeName": "name", "AttributeType": "S"},
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 10,
                    "WriteCapacityUnits": 10,
                },
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


Schools.table_name = "ncaa_schools"
Schools.dyn_resource = boto3.resource("dynamodb")

if table_exists(Schools.dyn_resource, Schools.table_name):
    Schools.table = get_table(Schools.dyn_resource, Schools.table_name)
else:
    Schools.table = Schools.create_table(Schools.dyn_resource, Schools.table_name)

if __name__ == "__main__":
    schools = Schools()

    schools.create_school("University of Alabama")
    schools.create_school("University of Georgia")
