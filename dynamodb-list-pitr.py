import boto3
import click

def describe_continuous_backups(table_name):
    """
    Describes the continuous backups of a DynamoDB table
    """
    dynamodb_client = boto3.client('dynamodb')
    response = dynamodb_client.describe_continuous_backups(TableName=table_name)
    recovery_description = response['ContinuousBackupsDescription']['PointInTimeRecoveryDescription']
    return recovery_description

def print_recovery_points(recovery_description):
    """
    Prints the available recovery points of a DynamoDB table
    """
    if recovery_description['PointInTimeRecoveryStatus'] == 'ENABLED':
        click.echo('Point-in-Time Recovery is enabled for the table.')
        click.echo('Available recovery points:')
        for recovery_point in recovery_description['EarliestRestorableDateTime'], recovery_description['LatestRestorableDateTime']:
            click.echo(recovery_point)
    else:
        click.echo('Point-in-Time Recovery is not enabled for the table.')

@click.command()
@click.option('--table-name', required=True, help='The name of the DynamoDB table')
def list_recovery_points(table_name):
    """
    Lists the available recovery points of a DynamoDB table
    """
    recovery_description = describe_continuous_backups(table_name)
    print_recovery_points(recovery_description)

if __name__ == '__main__':
    list_recovery_points()
