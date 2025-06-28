import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')
appointments_table = dynamodb.Table('appointments')
queue_table = dynamodb.Table('queue_status')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        location_id = body.get('location_id')
        date = body.get('date')

        if not location_id or not date:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "location_id and date are required"})
            }

        # Get current queue status
        queue = queue_table.get_item(Key={'location_id': location_id})
        current_token = queue.get('Item', {}).get('current_token', 0)
        next_token = current_token + 1

        # Find the matching appointment and update status
        response = appointments_table.scan(
            FilterExpression="location_id = :loc AND #d = :date AND #t = :tok",
            ExpressionAttributeNames={
                "#d": "date",
                "#t": "token"
            },
            ExpressionAttributeValues={
                ":loc": location_id,
                ":date": date,
                ":tok": next_token
            }
        )
        items = response['Items']
        if not items:
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "No more tokens to call"})
            }

        # Update appointment status
        appointment_id = items[0]['appointment_id']
        appointments_table.update_item(
            Key={'appointment_id': appointment_id},
            UpdateExpression="SET #s = :status",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":status": "called"}
        )

        # Update queue table
        queue_table.update_item(
            Key={'location_id': location_id},
            UpdateExpression="SET current_token = :val",
            ExpressionAttributeValues={":val": next_token}
        )

        lambda_client.invoke(
            FunctionName='notify_user',
            InvocationType='Event',
            Payload=json.dumps({
                "body": json.dumps({
                    "location_id": location_id,
                    "date": date
                })
            })
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Token {next_token} called successfully"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
