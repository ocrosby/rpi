import boto3
from botocore.exceptions import ClientError

from ripper.dal.logger import logger


def get_table(dyn_resource: boto3.resource, table_name: str) -> any:
    """
    Retrieves a DynamoDB table.

    :param table_name: The name of the table to retrieve.
    :return: The DynamoDB table.
    """
    try:
        table = dyn_resource.Table(table_name)
    except ClientError as err:
        logger.error(
            "Couldn't retrieve table %s. Here's why: %s: %s",
            table_name,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise

    return table


def delete_table(dyn_resource: boto3.resource, table_name: str):
    """
    Deletes an Amazon DynamoDB table.

    :param table_name: The name of the table to delete.
    """
    try:
        table = dyn_resource.Table(table_name)
        table.delete()
        table.wait_until_not_exists()
    except ClientError as err:
        logger.error(
            "Couldn't delete table %s. Here's why: %s: %s",
            table_name,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise


def table_exists(dyn_resource: boto3.resource, table_name: str) -> bool:
    """
    Checks if the table exists in DynamoDB

    :return: True if the table exists, False otherwise
    """
    try:
        dyn_resource.Table(table_name).load()
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return False
        raise

    return True
