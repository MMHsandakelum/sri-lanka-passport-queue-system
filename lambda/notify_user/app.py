import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')
appointments_table = dynamodb.Table('appointments')
queue_table = dynamodb.Table('queue_status')

def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return float(obj) if obj % 1 else int(obj)
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    return obj

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

        # Get current token from queue_status
        queue = queue_table.get_item(Key={'location_id': location_id})
        current_token = queue.get('Item', {}).get('current_token', 0)

        notify_token = current_token + 2

        # Find the appointment with this token
        response = appointments_table.scan(
            FilterExpression="location_id = :loc AND #d = :date AND #t = :tok",
            ExpressionAttributeNames={"#d": "date", "#t": "token"},
            ExpressionAttributeValues={
                ":loc": location_id,
                ":date": date,
                ":tok": notify_token
            }
        )

        items = response['Items']
        if not items:
            return {
                "statusCode": 200,
                "body": json.dumps({"message": f"No upcoming user found for token {notify_token}"})
            }

        user = items[0]
        email = user['email']
        token = user['token']

        # Send email
        subject = f"Your Passport Token #{token} is Almost Ready!"
        body_text = (
            f"Dear user,\n\n"
            f"Your token number {token} will be called soon at {location_id.upper()} office on {date}.\n"
            "Please be prepared to approach the counter.\n\n"
            "Thank you!"
        )

        ses.send_email(
            Source="mmharshasandakelum@gmail.com",
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body_text}}
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Notification sent to {email}"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }