# import boto3
# import click
# from datetime import datetime


# def get_table_properties(table_name):
#     """
#     Gets the properties of a DynamoDB table
#     """
#     dynamodb_client = boto3.client('dynamodb')
#     try:
#         response = dynamodb_client.describe_table(TableName=table_name)
#         table = response['Table']
#         return {
#             'BillingMode': table.get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED'),
#             'ProvisionedThroughput': table['ProvisionedThroughput'],
#             'AttributeDefinitions': table['AttributeDefinitions'],
#             'KeySchema': table['KeySchema'],
#             'LocalSecondaryIndexes': table.get('LocalSecondaryIndexes', []),
#             'GlobalSecondaryIndexes': table.get('GlobalSecondaryIndexes', [])
#         }
#     except dynamodb_client.exceptions.ResourceNotFoundException:
#         raise click.ClickException(f"Table {table_name} does not exist.")

# # # def restore_table(table_name, restore_time, target_table_name):
# # #     """
# # #     Restores a DynamoDB table to a specified time
# # #     """
# # #     dynamodb_client = boto3.client('dynamodb')
# # #     try:
# # #         old_table_properties = get_table_properties(table_name)
# # #         response = dynamodb_client.restore_table_to_point_in_time(
# # #             SourceTableName=table_name,
# # #             TargetTableName=target_table_name,
# # #             RestoreDateTime=restore_time,
# # #             BillingModeOverride=old_table_properties.get('BillingMode', 'PROVISIONED')
# # #         )
# # #         click.echo('Restore request initiated for the table.')
# # #     except dynamodb_client.exceptions.ResourceNotFoundException:
# # #         raise click.ClickException(f"Table {table_name} does not exist.")

# # def restore_table(table_name, restore_time, target_table_name=None, billing_mode_override=None):
# #     """
# #     Restore the given DynamoDB table to a point in time.

# #     :param table_name: The name of the table to restore.
# #     :param restore_time: The timestamp to which the table should be restored, in Unix time format.
# #     :param target_table_name: The name of the restored table. If not provided, a default name will be used.
# #     :param billing_mode_override: Override the billing mode of the restored table. Valid values are "PROVISIONED" and
# #     "PAY_PER_REQUEST". If set to "PROVISIONED", you must also provide a ProvisionedThroughputOverride dict.
# #     :return: None
# #     """
# #     dynamodb_client = boto3.client('dynamodb')
# #     # If no target table name is provided, use a default name.
# #     if target_table_name is None:
# #         target_table_name = f"{table_name}-restored"

# #     # If billing mode override is provided, validate the input and create the necessary arguments.
# #     billing_args = {}
# #     if billing_mode_override is not None:
# #         if billing_mode_override == "PAY_PER_REQUEST":
# #             billing_args["BillingModeOverride"] = billing_mode_override
# #         elif billing_mode_override == "PROVISIONED":
# #             if "ProvisionedThroughputOverride" not in billing_mode_override:
# #                 raise ValueError("Must provide ProvisionedThroughputOverride when overriding billing mode to PROVISIONED.")
# #             billing_args = billing_mode_override
# #         else:
# #             raise ValueError(f"Invalid value for billing_mode_override: {billing_mode_override}")

# #     # Restore the table to the specified point in time.
# #     response = dynamodb_client.restore_table_to_point_in_time(
# #         SourceTableName=table_name,
# #         TargetTableName=target_table_name,
# #         RestoreDateTime=datetime.fromtimestamp(restore_time),
# #         **billing_args
# #     )
# #     print(f"Table restore started for {table_name}.")
# #     print(f"Restored table name: {response['TableDescription']['TableName']}")
# #     print(f"Restored table ARN: {response['TableDescription']['TableArn']}")
# #     print(f"Restored table status: {response['TableDescription']['TableStatus']}")
# #     print(f"Restored table billing mode: {response['TableDescription']['BillingModeSummary']['BillingMode']}")
# #     return None

# import boto3

# def restore_table(table_name, restore_time, target_table_name):
#     client = boto3.client('dynamodb')
#     response = client.describe_table(
#         TableName=table_name
#     )
#     table = response['Table']
    
#     # Create the restored table with the same properties as the original table
#     attribute_definitions = table['AttributeDefinitions']
#     key_schema = table['KeySchema']
#     provisioned_throughput = table['ProvisionedThroughput']
#     global_secondary_indexes = table.get('GlobalSecondaryIndexes')
#     local_secondary_indexes = table.get('LocalSecondaryIndexes')
#     stream_specification = table.get('StreamSpecification')
#     billing_mode = table.get('BillingMode')
#     tags = client.list_tags_of_resource(ResourceArn=table['TableArn']).get('Tags', [])
    
#     if billing_mode == 'PROVISIONED':
#         restored_table = client.create_table(
#             TableName=target_table_name,
#             AttributeDefinitions=attribute_definitions,
#             KeySchema=key_schema,
#             ProvisionedThroughput=provisioned_throughput,
#             GlobalSecondaryIndexes=global_secondary_indexes,
#             LocalSecondaryIndexes=local_secondary_indexes,
#             StreamSpecification=stream_specification,
#             Tags=tags
#         )
#     else:
#         restored_table = client.create_table(
#             TableName=target_table_name,
#             AttributeDefinitions=attribute_definitions,
#             KeySchema=key_schema,
#             BillingMode=billing_mode,
#             GlobalSecondaryIndexes=global_secondary_indexes,
#             LocalSecondaryIndexes=local_secondary_indexes,
#             StreamSpecification=stream_specification,
#             Tags=tags
#         )
    
#     # Wait for the restored table to become available
#     waiter = client.get_waiter('table_exists')
#     waiter.wait(
#         TableName=target_table_name,
#         WaiterConfig={
#             'Delay': 30,
#             'MaxAttempts': 20
#         }
#     )

#     # Enable Point-In-Time Recovery
#     client.update_continuous_backups(
#         TableName=target_table_name,
#         PointInTimeRecoverySpecification={
#             'PointInTimeRecoveryEnabled': True
#         }
#     )

#     # Wait for Point-In-Time Recovery to become enabled
#     waiter = client.get_waiter('table_exists')
#     waiter.wait(
#         TableName=target_table_name,
#         WaiterConfig={
#             'Delay': 30,
#             'MaxAttempts': 20
#         }
#     )

#     # Update the restored table with the same properties as the original table
#     client.update_table(
#         TableName=target_table_name,
#         AttributeDefinitions=attribute_definitions,
#         BillingMode=billing_mode,
#         ProvisionedThroughput=provisioned_throughput,
#         GlobalSecondaryIndexUpdates=global_secondary_indexes,
#         LocalSecondaryIndexUpdates=local_secondary_indexes,
#         StreamSpecification=stream_specification
#     )

    
# def wait_for_restore_to_complete(target_table_name):
#     """
#     Waits for the restore operation to complete
#     """
#     dynamodb_client = boto3.client('dynamodb')
#     waiter = dynamodb_client.get_waiter('table_exists')
#     waiter.wait(TableName=target_table_name)

# def rename_table(table_name, new_table_name):
#     """
#     Renames a DynamoDB table
#     """
#     dynamodb_client = boto3.client('dynamodb')
#     dynamodb_client.update_table(TableName=table_name,
#                                   NewTableName=new_table_name)

# @click.command()
# @click.option('--table-name', required=True, help='The name of the DynamoDB table')
# @click.option('--restore-time', required=True, help='The time to restore the table to, in the ISO 8601 format')
# def restore_dynamodb_table(table_name, restore_time):
#     """
#     Restores a DynamoDB table to a specified time and renames the old table and the restored table
#     """
#     target_table_name = table_name + '-restored'
#     restore_table(table_name, restore_time, target_table_name)
#     click.echo('Restoring the Table...')

#     click.echo('Wait for Table to Restore...')
#     wait_for_restore_to_complete(target_table_name)
#     click.echo('Restored Successfully')
    
#     # old_table_name = table_name + '-old'
#     # rename_table(table_name, old_table_name)
#     # click.echo('Old table renamed to ' + old_table_name)

#     # rename_table(target_table_name, table_name)
#     # click.echo('Restored table renamed to ' + table_name)

# if __name__ == '__main__':
#     restore_dynamodb_table()
