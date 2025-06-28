import json
import uuid
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
appointments_table = dynamodb.Table('appointments')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])

        nic = body['nic']
        name = body.get('name', '')
        email = body['email']
        location_id = body['location_id']
        date = body['date']       
        time = body['time']

        # Generate appointment ID and token
        appointment_id = str(uuid.uuid4())

        # Count existing appointments for this time slot
        response = appointments_table.scan(
            FilterExpression='location_id = :loc AND #d = :date AND #t = :time',
            ExpressionAttributeNames={
                '#d': 'date',
                '#t': 'time'
            },
            ExpressionAttributeValues={
                ':loc': location_id,
                ':date': date,
                ':time': time
            }
        )
        current_count = len(response['Items'])
        token_number = current_count + 1

        # Store new appointment
        appointments_table.put_item(
            Item={
                'appointment_id': appointment_id,
                'nic': nic,
                'name': name,
                'email': email,
                'location_id': location_id,
                'date': date,
                'time': time,
                'token': token_number,
                'status': 'waiting',
                'created_at': datetime.utcnow().isoformat()
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Appointment booked successfully',
                'appointment_id': appointment_id,
                'token': token_number
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }