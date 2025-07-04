import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
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
        # Parse query string parameters
        params = event.get("queryStringParameters") or {}
        location_id = params.get("location_id")
        date = params.get("date")

        if not location_id or not date:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "location_id and date are required"})
            }

        # Get appointments for location/date that are still waiting
        response = appointments_table.scan(
            FilterExpression="location_id = :loc AND #d = :date AND #s = :status",
            ExpressionAttributeNames={
                "#d": "date",
                "#s": "status"
            },
            ExpressionAttributeValues={
                ":loc": location_id,
                ":date": date,
                ":status": "waiting"
            }
        )
        waiting = sorted(response["Items"], key=lambda x: x.get("token", 0))

        # Get current token from queue_status table
        qres = queue_table.get_item(Key={"location_id": location_id})
        current_token = qres.get("Item", {}).get("current_token", 0)

        result = {
            "current_token": current_token,
            "waiting_count": len(waiting),
            "waiting_list": [
                {"token": appt["token"], "time": appt["time"]} for appt in waiting
            ]
        }

        return {
            "statusCode": 200,
            "body": json.dumps(convert_decimal(result))
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }