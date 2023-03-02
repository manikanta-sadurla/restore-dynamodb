import boto3
import click

def restore_table(table_name, restore_time, target_table_name):
    """
    Restores a DynamoDB table to a specified time
    """
    dynamodb_client = boto3.client('dynamodb')
    response = dynamodb_client.restore_table_to_point_in_time(
        SourceTableName=table_name,
        TargetTableName=target_table_name,
        RestoreDateTime=restore_time
    )
    click.echo('Restore request initiated for the table.')

def wait_for_restore_to_complete(target_table_name):
    """
    Waits for the restore operation to complete
    """
    dynamodb_client = boto3.client('dynamodb')
    waiter = dynamodb_client.get_waiter('table_exists')
    waiter.wait(TableName=target_table_name)

def rename_table(table_name, new_table_name):
    """
    Renames a DynamoDB table
    """
    dynamodb_client = boto3.client('dynamodb')
    dynamodb_client.update_table(TableName=table_name,
                                  NewTableName=new_table_name)

@click.command()
@click.option('--table-name', required=True, help='The name of the DynamoDB table')
@click.option('--restore-time', required=True, help='The time to restore the table to, in the ISO 8601 format')
def restore_dynamodb_table(table_name, restore_time):
    """
    Restores a DynamoDB table to a specified time and renames the old table and the restored table
    """
    target_table_name = table_name + '-restored'
    restore_table(table_name, restore_time, target_table_name)
    click.echo('Restoring the Table...')

    click.echo('Wait for Table to Restore...')
    wait_for_restore_to_complete(target_table_name)
    click.echo('Restored Successfully')
    
    # old_table_name = table_name + '-old'
    # rename_table(table_name, old_table_name)
    # click.echo('Old table renamed to ' + old_table_name)

    # rename_table(target_table_name, table_name)
    # click.echo('Restored table renamed to ' + table_name)

if __name__ == '__main__':
    restore_dynamodb_table()
